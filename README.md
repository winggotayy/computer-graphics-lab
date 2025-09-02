# Computer Graphics Lab: Basic Graphics Rendering and Transformation System

![Python](https://img.shields.io/badge/language-Python-blue.svg)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)

## 📚 Project Documentation & Demo

### 📋 Technical Reports
- **[Detailed Technical Report](205220025_报告.pdf)** - Contains algorithm principles, implementation details, and performance analysis
- **[System User Manual](205220025_说明书.pdf)** - Complete user guide and operating instructions

### 🎥 Demo
- **[Feature Demo Video](https://drive.google.com/file/d/1kmmXjXS1-yiGBtPbBKYDq8FVZwtodpT5/view?usp=drive_link)** - Complete system functionality demonstration

## 🎯 Overview

This project is a complete computer graphics system developed as part of the Computer Graphics course. It implements fundamental 2D graphics algorithms including line drawing, curve generation, geometric transformations, and line clipping operations. The system provides both command-line interface (CLI) and graphical user interface (GUI) for interactive graphics manipulation.

## ✨ Features

### 🎨 Primitive Drawing
- **Line Drawing**: Naïve, DDA, and Bresenham algorithms
- **Polygon Drawing**: DDA and Bresenham algorithms
- **Ellipse Drawing**: Midpoint ellipse generation algorithm
- **Curve Drawing**:
  - Bezier curves (De Casteljau algorithm)
  - B-spline curves (De Boor-Cox algorithm)

### 🔄 Geometric Transformations
- **Translation**: Move primitives by offset values
- **Rotation**: Rotate primitives around any center point
- **Scaling**: Scale primitives with customizable center and factor

### ✂️ Line Clipping
- **Cohen-Sutherland algorithm**: Region-code based clipping
- **Liang-Barsky algorithm**: Parametric line clipping

### 💻 Interface
- **CLI Mode**: Batch processing of drawing commands from input files
- **GUI Mode**: Interactive drawing and manipulation with PyQt5
- **Canvas Management**: Reset, save, open, and modify canvas properties
- **Visual Feedback**: Selected primitives highlighted with red bounding boxes

## 🛠️ Implementation Details

### Technical Stack
- **Python 3.12.4** with NumPy for mathematical operations
- **PyQt5** for graphical user interface
- **PIL/Pillow** for image saving and manipulation
- **Pickle** for canvas state serialization

### Algorithm Highlights
- **Bresenham's Line Algorithm**: Integer-only operations for efficiency
- **Midpoint Ellipse Algorithm**: Divided into two regions for optimal point generation
- **De Casteljau Algorithm**: Recursive interpolation for Bezier curves
- **De Boor-Cox Algorithm**: Dynamic programming approach for B-spline basis functions
- **Liang-Barsky Optimization**: Parameter-based clipping with reduced computations

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PyQt5
- NumPy
- Pillow

### Installation
1. Clone the repository:
```bash
git clone https://github.com/winggotayy/computer-graphics-lab.git
cd computer-graphics-lab
```

2. Usage

GUI Mode (Interactive):
```bash
python main.py
```

CLI Mode (Batch Processing):
```bash
python cg_cli.py input.txt output
```

## 📖 Usage Examples

### Drawing Primitives
1. Select a drawing tool (Line, Polygon, Ellipse, Curve)
2. Choose an algorithm from the menu
3. Click and drag on canvas to create shapes

### Applying Transformations
1. Enter selection mode and click on a primitive
2. Choose transformation type (Translate, Rotate, Scale)
3. Interactively manipulate the selected primitive

### Line Clipping
1. Select a line primitive
2. Choose clipping algorithm
3. Define clipping window by dragging on canvas

🎨 Interface Overview
The GUI provides:

Menu Bar: File operations and algorithm selection

Toolbar: Quick access to common functions

Canvas: Interactive drawing area

Primitive List: Overview of all drawn objects

Status Bar: Current operation information
