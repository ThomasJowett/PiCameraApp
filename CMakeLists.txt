cmake_minimum_required(VERSION 3.0)

Project(PiCameraApp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt5 COMPONENTS Core Widgets REQUIRED)
find_package(OpenCV REQUIRED)

set(SOURCES
    src/main.cpp
)

include_directories(
    ${Qt5Widgets_INCLUDE_DIRS}
)

add_executable(PiCameraApp ${SOURCES} ${HEADERS})

target_link_libraries(PiCameraApp Qt5::Core Qt5::Widgets ${OpenCV_LIBS})
