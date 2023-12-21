
#include <iostream>
#include <QApplication>
#include <QWidget>
#include <QPushButton>
#include <QMessageBox>

class FullScreenWindow : public QWidget {
public:
    FullScreenWindow(QWidget*parent = nullptr) : QWidget(parent) {
        QPushButton *button = new QPushButton("Take picture", this);
        connect(button, &QPushButton::clicked, this, &FullScreenWindow::onTakePictureClicked);

        button->setFixedSize(200, 50);
        button->move((width() - button->width()) / 2, (height() - button->height()) / 2);
    }

private slots:
    void onTakePictureClicked() {
        QMessageBox::information(this, "Picture Taken", "Picture has been taken!");
    }
};

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    FullScreenWindow window;
    window.showFullScreen();

    return app.exec();
}