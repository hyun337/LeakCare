import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
import os


# BiSeNet 원본 구조
class ConvBNReLU(nn.Module):
    def __init__(self, in_chan, out_chan, ks=3, stride=1, padding=1):
        super().__init__()
        self.conv = nn.Conv2d(
            in_chan, out_chan,
            kernel_size=ks,
            stride=stride,
            padding=padding,
            bias=False
        )
        self.bn = nn.BatchNorm2d(out_chan)

    def forward(self, x):
        return F.relu(self.bn(self.conv(x)))


class AttentionRefinementModule(nn.Module):
    def __init__(self, in_chan, out_chan):
        super().__init__()
        self.conv = ConvBNReLU(in_chan, out_chan)
        self.conv_atten = nn.Conv2d(out_chan, out_chan, kernel_size=1, bias=False)
        self.bn_atten = nn.BatchNorm2d(out_chan)

    def forward(self, x):
        feat = self.conv(x)
        atten = torch.mean(feat, dim=(2, 3), keepdim=True)
        atten = self.bn_atten(self.conv_atten(atten))
        atten = torch.sigmoid(atten)
        return feat * atten


class ContextPath(nn.Module):
    def __init__(self):
        super().__init__()
        self.resnet = models.resnet18(weights=None)
        self.arm16 = AttentionRefinementModule(256, 128)
        self.arm32 = AttentionRefinementModule(512, 128)
        self.conv_head32 = ConvBNReLU(128, 128)
        self.conv_head16 = ConvBNReLU(128, 128)
        self.conv_avg = ConvBNReLU(512, 128, ks=1, padding=0)

    def forward(self, x):
        x = self.resnet.relu(self.resnet.bn1(self.resnet.conv1(x)))
        x = self.resnet.maxpool(x)
        x = self.resnet.layer1(x)
        feat8 = self.resnet.layer2(x)
        feat16 = self.resnet.layer3(feat8)
        feat32 = self.resnet.layer4(feat16)

        avg = torch.mean(feat32, dim=(2, 3), keepdim=True)
        avg = self.conv_avg(avg)
        avg_up = F.interpolate(avg, size=feat32.shape[2:], mode='nearest')

        feat32_arm = self.arm32(feat32)
        feat32_sum = feat32_arm + avg_up
        feat32_up = F.interpolate(feat32_sum, size=feat16.shape[2:], mode='nearest')
        feat32_up = self.conv_head32(feat32_up)

        feat16_arm = self.arm16(feat16)
        feat16_sum = feat16_arm + feat32_up
        feat16_up = F.interpolate(feat16_sum, size=feat8.shape[2:], mode='nearest')
        feat16_up = self.conv_head16(feat16_up)

        return feat8, feat16_up, feat32_up


class FeatureFusionModule(nn.Module):
    def __init__(self, in_chan, out_chan):
        super().__init__()
        self.convblk = ConvBNReLU(in_chan, out_chan, ks=1, padding=0)
        self.conv1 = nn.Conv2d(out_chan, out_chan // 4, kernel_size=1, bias=False)
        self.conv2 = nn.Conv2d(out_chan // 4, out_chan, kernel_size=1, bias=False)

    def forward(self, fsp, fcp):
        fcat = torch.cat([fsp, fcp], dim=1)
        feat = self.convblk(fcat)
        atten = torch.mean(feat, dim=(2, 3), keepdim=True)
        atten = F.relu(self.conv1(atten))
        atten = torch.sigmoid(self.conv2(atten))
        return feat + feat * atten


class SpatialPath(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = ConvBNReLU(3, 64, stride=2)
        self.conv2 = ConvBNReLU(64, 64, stride=2)
        self.conv3 = ConvBNReLU(64, 64, stride=2)
        self.conv_out = ConvBNReLU(64, 128, ks=1, padding=0)

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        return self.conv_out(x)


class BiSeNetOutput(nn.Module):
    def __init__(self, in_chan, mid_chan, n_classes):
        super().__init__()
        self.conv = ConvBNReLU(in_chan, mid_chan)
        self.conv_out = nn.Conv2d(mid_chan, n_classes, kernel_size=1, bias=False)

    def forward(self, x):
        x = self.conv(x)
        return self.conv_out(x)


class BiSeNet(nn.Module):
    def __init__(self, n_classes=19):
        super().__init__()
        self.cp = ContextPath()
        self.ffm = FeatureFusionModule(256, 256)
        self.conv_out = BiSeNetOutput(256, 256, n_classes)
        self.conv_out16 = BiSeNetOutput(128, 64, n_classes)
        self.conv_out32 = BiSeNetOutput(128, 64, n_classes)

    def forward(self, x):
        H, W = x.shape[2:]
        feat_res8, feat_cp8, feat_cp16 = self.cp(x)

        feat_fuse = self.ffm(feat_res8, feat_cp8)
        feat_out = self.conv_out(feat_fuse)
        feat_out = F.interpolate(feat_out, size=(H, W), mode='bilinear', align_corners=True)

        feat_out16 = self.conv_out16(feat_cp8)
        feat_out32 = self.conv_out32(feat_cp16)

        return feat_out, feat_out16, feat_out32


# Face Parsing 레이블
SKIN_LABEL = 1
LEFT_EYE_LABEL = 4
RIGHT_EYE_LABEL = 5
NOSE_LABEL = 10
MOUTH_LABEL = 11
UPPER_LIP_LABEL = 12
LOWER_LIP_LABEL = 13

# Threshold 설정값
EYE_THRESHOLD = 0.001
NOSE_THRESHOLD = 0.01
MOUTH_THRESHOLD = 0.001


class FaceParser:
    def __init__(self, model_path=None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_path = os.path.join(base_dir, "models", "face_parsing.pth")

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model(model_path)

    def _load_model(self, model_path):
        if not os.path.exists(model_path):
            print(f"모델 파일이 없습니다: {model_path}")
            return None

        try:
            model = BiSeNet(n_classes=19)
            state_dict = torch.load(model_path, map_location=self.device, weights_only=True)
            model.load_state_dict(state_dict, strict=False)
            model.to(self.device)
            model.eval()
            return model
        except Exception as e:
            print(f"모델 로드 실패: {e}")
            return None

    def parse(self, face_image):
        if self.model is None:
            return None

        img = cv2.resize(face_image, (512, 512))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = (img - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        img = img.transpose(2, 0, 1)
        img = torch.from_numpy(img).unsqueeze(0).float().to(self.device)

        with torch.no_grad():
            output = self.model(img)
            if isinstance(output, tuple):
                output = output[0]
            parsing = output.argmax(1).squeeze().cpu().numpy()

        return parsing

    def check_occlusion(self, face_image):
        if self.model is None:
            return {
                "pass": False,
                "eye_visible": True,
                "nose_visible": True,
                "mouth_visible": True,
                "eye_ratio": 0,
                "nose_ratio": 0,
                "mouth_ratio": 0,
                "message": "Face Parsing 모델 없음"
            }

        parsing = self.parse(face_image)
        if parsing is None:
            return {
                "pass": True,
                "eye_visible": True,
                "nose_visible": True,
                "mouth_visible": True,
                "eye_ratio": 0,
                "nose_ratio": 0,
                "mouth_ratio": 0,
                "message": "파싱 실패 (통과 처리)"
            }

        # 배경 제외한 얼굴 기준 픽셀 수
        background_pixels = np.sum(parsing == 0)
        face_pixels = parsing.size - background_pixels
        base = face_pixels if face_pixels > 0 else parsing.size

        # 눈, 코, 입 픽셀 수 계산
        eye_pixels = np.sum(
            (parsing == LEFT_EYE_LABEL) |
            (parsing == RIGHT_EYE_LABEL)
        )

        nose_pixels = np.sum(parsing == NOSE_LABEL)

        mouth_pixels = np.sum(
            (parsing == MOUTH_LABEL) |
            (parsing == UPPER_LIP_LABEL) |
            (parsing == LOWER_LIP_LABEL)
        )

        # 비율 계산
        eye_ratio = eye_pixels / base
        nose_ratio = nose_pixels / base
        mouth_ratio = mouth_pixels / base

        # visibility 판단
        eye_visible = eye_ratio > EYE_THRESHOLD
        nose_visible = nose_ratio > NOSE_THRESHOLD
        mouth_visible = mouth_ratio > MOUTH_THRESHOLD

        # 최종 통과 조건
        is_pass = eye_visible and nose_visible and mouth_visible

        issues = []
        if not eye_visible:
            issues.append("눈이 충분히 보이지 않습니다")
        if not nose_visible:
            issues.append("코가 충분히 보이지 않습니다")
        if not mouth_visible:
            issues.append("입이 충분히 보이지 않습니다")

        if is_pass:
            message = "눈/코/입 모두 확인 가능"
        else:
            message = ", ".join(issues) + ". 가림 없는 정면 사진을 등록해주세요."
            
            # 👈 이 print문을 추가해서 수치를 확인해보세요!
            print(f"--- [AI 검증 수치] ---")
            print(f"눈 가림 비율: {eye_ratio:.4f} (기준: {EYE_THRESHOLD})")
            print(f"코 가림 비율: {nose_ratio:.4f} (기준: {NOSE_THRESHOLD})")
            print(f"입 가림 비율: {mouth_ratio:.4f} (기준: {MOUTH_THRESHOLD})")
            
            # ... (이후 결과 반환) ...
        return {
            "pass": is_pass,
            "eye": eye_visible,
            "nose": nose_visible,
            "mouth": mouth_visible,
            "eye_ratio": round(float(eye_ratio), 4),
            "nose_ratio": round(float(nose_ratio), 4),
            "mouth_ratio": round(float(mouth_ratio), 4),
            "message": message
        }

# 테스트
if __name__ == "__main__":
    parser = FaceParser()

    test_image_path = "../../data/test_images/shm3.png"

    if os.path.exists(test_image_path):
        image = cv2.imread(test_image_path)

        result = parser.check_occlusion(image)
        print(result['pass'])
        print(f"눈: {result['eye']}, {result['eye_ratio']}")
        print(f"코: {result['nose']}, {result['nose_ratio']}")
        print(f"입: {result['mouth']}, {result['mouth_ratio']}")
        print(result['message'])
    else:
        print(f"테스트 이미지가 없습니다: {test_image_path}")