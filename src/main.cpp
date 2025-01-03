#include <iostream>
#include <QApplication>
#include <QWidget>
#include <QPushButton>
#include <QMessageBox>
#include <QVBoxLayout>
#include <QLabel>
#include <QTimer>
#include <opencv2/opencv.hpp>

class FullScreenWindow : public QWidget{
public:
    FullScreenWindow(QWidget*parent = nullptr) : QWidget(parent) {
        setWindowTitle("Camera Preview");
        QVBoxLayout *layout = new QVBoxLayout(this);

        videoLabel = new QLabel(this);
        layout->addWidget(videoLabel);

        QPushButton *button = new QPushButton("Take picture", this);
        connect(button, &QPushButton::clicked, this, &FullScreenWindow::onTakePictureButtonClicked);
        layout->addWidget(button);

        button->setFixedSize(200, 50);
        button->move((width() - button->width()) / 2, (height() - button->height()) / 2);

        cap.open(0, cv::CAP_V4L2);
        if(!cap.isOpened()){
            throw std::runtime_error("Could not open camera");
        }

        cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
        cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);
        cap.set(cv::CAP_PROP_FOURCC, cv::VideoWriter::fourcc('M', 'J', 'P', 'G'));

        cv::Mat frame;
        while (true)
        {
            cap >> frame;
            if(frame.empty()){
                std::cerr << "Error: Empty frame captured" << std::endl;
            }
            cv::imshow("Camera feed", frame);
            if(cv::waitKey(30) >= 0) break;
        }

        QTimer *timer = new QTimer(this);
        connect(timer, &QTimer::timeout, this, &FullScreenWindow::updateFrame);
        timer->start(30);
    }

private slots:
	void updateFrame() {
        cv::Mat frame;
		cap >> frame;
		if(frame.empty()) {
			return;
		}
		cv::cvtColor(frame, frame, cv::COLOR_BGR2RGB);
		QImage image = QImage((const unsigned char*)frame.data, frame.cols, frame.rows, frame.step[0], QImage::Format_RGB888);
        std::cout << frame.cols << " " << frame.rows << std::endl;

        videoLabel->setPixmap(QPixmap::fromImage(image));
	}
    void onTakePictureButtonClicked() {
        cv::Mat frame;
        cap >> frame;

        if(!frame.empty()){
            cv::imwrite("picture.jpg", frame);
            QMessageBox::information(this, "Picture Taken", "Picture has been taken!");
        } else {
            QMessageBox::critical(this, "Error", "Failed to capture image");
        }
    }
private:
	cv::VideoCapture cap;
	QLabel *videoLabel;
};

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    FullScreenWindow window;
    window.showFullScreen();

    return app.exec();
}
