const video = document.getElementById('video');
const canvas = document.getElementById('overlay');
const context = canvas.getContext('2d');
const socket = io.connect('http://localhost:5000', { transports: ['websocket'] });

function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
            video.play();
            setInterval(sendFrameToServer, 100);  // Belirli aralıklarla sunucuya gönder
        })
        .catch((error) => {
            console.error("Kamera açılırken bir hata oluştu:", error);
            alert("Kamera açılırken bir hata oluştu. İzinleri kontrol edin.");
        });
}

function sendFrameToServer() {
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const tempContext = tempCanvas.getContext('2d');
    tempContext.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
    const frameData = tempCanvas.toDataURL('image/jpeg').split(',')[1];
    socket.emit('video_frame', { frame: frameData });
}

socket.on('processed_frame', function (data) {
    const img = new Image();
    img.onload = function () {
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
    img.src = 'data:image/jpeg;base64,' + data.frame;
});
