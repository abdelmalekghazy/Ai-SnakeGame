import cv2
import math
import random
import cvzone
from cvzone.HandTrackingModule import HandDetector

# Kamera ayarları
cap = cv2.VideoCapture(0)
cap.set(3, 800)  # Genişlik ayarı
cap.set(4, 600)  # Yükseklik ayarı

# El tespiti için HandDetector nesnesi oluşturma
detector = HandDetector(detectionCon=0.7, maxHands=1)

# Yılan Oyunu sınıfı
class SnakeGame:
    def __init__(self, pathFood):
        self.points = []  # Yılanın noktaları
        self.length = []  # Her bir nokta arasındaki mesafeler
        self.currentLenght = 0  # Mevcut yılan uzunluğu
        self.allowedLength = 100  # İzin verilen başlangıç uzunluğu
        self.perviousHead = 0, 0  # Önceki baş noktası
        
        self.imageFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)  # Yiyecek resmi
        self.hFood, self.wFood, _ = self.imageFood.shape
        self.foodPoints = 0, 0
        self.randomFoodLocation()  # Rastgele yiyecek konumu belirleme

    def randomFoodLocation(self):
        self.foodPoints = random.randint(100, 600), random.randint(100, 400)  # Rastgele yiyecek konumu

    def update(self, imgMain, currentHead):
        px, py = self.perviousHead
        cx, cy = currentHead
        self.points.append([cx, cy])  # Yılanın yeni baş noktasını ekle
        distance = math.hypot(cx - px, cy - py)  # İki nokta arasındaki mesafeyi hesapla
        self.length.append(distance)  # Mesafeyi yılanın uzunluğuna ekle
        self.currentLenght += distance
        self.perviousHead = cx, cy  # Önceki baş noktasını güncelle

        # Yılanın uzunluğunu kontrol etme ve izin verilen uzunluğu aşarsa eski noktaları kaldırma
        if self.currentLenght > self.allowedLength:
            for i, length in enumerate(self.length):
                self.currentLenght -= length
                self.length.pop(i)
                self.points.pop(i)
                if self.currentLenght < self.allowedLength:
                    break

        # Yılan yiyeceğe temas ederse
        rx, ry = self.foodPoints
        if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and ry - self.hFood // 2 < cy < ry + self.hFood // 2:
            self.randomFoodLocation()  # Yeni yiyecek konumu belirle
            self.allowedLength += 25  # Yılanın uzunluğunu artır

        # Yılanın çizimi
        if self.points:
            for i, points in enumerate(self.points):
                if i != 0:
                    cv2.line(imgMain, self.points[i-1], self.points[i], (0, 0, 255), 20)  # Yılanın gövdesi
                    cv2.circle(imgMain, self.points[-1], 20, (200, 0, 200), cv2.FILLED)  # Yılanın başı

            rx, ry = self.foodPoints
            imgMain = cvzone.overlayPNG(imgMain, self.imageFood, (rx-self.wFood // 2, ry-self.hFood // 2))  # Yiyecek resmi

        return imgMain

# Yılan oyunu nesnesi oluşturma
game = SnakeGame('apple.png')

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # Görüntüyü yatay olarak çevir
    hands, img = detector.findHands(img, flipType=False)  # Elleri tespit et

    if hands:
        lmList = hands[0]['lmList']
        pointIndex = lmList[8][0:2]  # İşaret parmağının ucu
        img = game.update(img, pointIndex)  # Oyunu güncelle

    cv2.imshow("Snake Game [python ai]", img)  # Görüntüyü göster
    key = cv2.waitKey(1)
