import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from GUI import Ui_MainWindow
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import os
import numpy

surfaceExtractor = vtk.vtkContourFilter()


def slider_SLOT(val):
    surfaceExtractor.SetValue(0, val)
    
    QApplication.processEvents()
    iren.update()
    


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.isoValue.valueChanged.connect(slider_SLOT)
        self.ui.opacity.valueChanged.connect(self.Ray_casting)
        self.ui.load.clicked.connect(self.load)
        self.ui.modul_comboBox.currentIndexChanged.connect(self.select)
        self.show()

    def load(self):
        self.select_dir()
        QApplication.processEvents()
        self.dir = self.folder
        QApplication.processEvents()

    def select_dir(self):
        self.folder = QFileDialog.getExistingDirectory(self)

    def select(self):
        if (self.ui.modul_comboBox.currentText() == "Surface rendering"):
            self.Surface()
        elif (self.ui.cmodul_comboBox.currentText() == "Ray casting rendering"):
            self.Ray_casting()

    def Ray_casting(self):
        renWin = iren.GetRenderWindow()
        self.aRenderer = vtk.vtkRenderer()
        renWin.AddRenderer(self.aRenderer)
        self.v16 = vtk.vtkDICOMImageReader()
        self.v16.SetDirectoryName(self.dir)
        self.v16.Update()
        shifter = vtk.vtkImageShiftScale()
        offset = self.v16.GetRescaleOffset()
        slope = self.v16.GetRescaleSlope()
        shifter.SetScale(slope)
        shifter.SetShift(-1 * offset)
        shifter.SetInputConnection(self.v16.GetOutputPort())
        # ray
        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputConnection(shifter.GetOutputPort())
        volumeMapper.SetBlendModeToComposite()

        # color
        volumeColor = vtk.vtkColorTransferFunction()
        volumeColor.AddRGBPoint(0, 0.0, 0.0, 0.0)
        volumeColor.AddRGBPoint(500, 1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(1000, 1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(1150, 1.0, 1.0, 0.9)

        # The opacity transfer function
        volumeScalarOpacity = vtk.vtkPiecewiseFunction()
        volumeScalarOpacity.AddPoint(0, 0.00)
        volumeScalarOpacity.AddPoint(500, 0.15)
        volumeScalarOpacity.AddPoint(1000, 0.15)
        volumeScalarOpacity.AddPoint(1150, 0.85)

        # The gradient opacity function is used to decrease the opacity
        volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(0, 0.0)
        volumeGradientOpacity.AddPoint(90,self.ui.opacity.value()/100)
        volumeGradientOpacity.AddPoint(100, 1.0)

        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(volumeColor)
        volumeProperty.SetScalarOpacity(volumeScalarOpacity)
        volumeProperty.SetGradientOpacity(volumeGradientOpacity)
        volumeProperty.SetInterpolationTypeToLinear()
        volumeProperty.ShadeOn()
        volumeProperty.SetAmbient(0.4)
        volumeProperty.SetDiffuse(0.6)
        volumeProperty.SetSpecular(0.2)

        # The vtkVolume is a vtkProp3D (like a vtkActor) and controls the position
        # and orientation of the volume in world coordinates.
        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)

        self.aRenderer.AddViewProp(volume)
        aCamera = vtk.vtkCamera()
        aCamera.SetViewUp(0, 0, -1)
        aCamera.SetPosition(0, 1, 0)
        aCamera.SetFocalPoint(0, 0, 0)
        aCamera.ComputeViewPlaneNormal()

        self.aRenderer.SetActiveCamera(aCamera)
        self.aRenderer.ResetCamera()

        self.aRenderer.SetBackground(0, 0, 0)

        self.aRenderer.ResetCameraClippingRange()

        # Interact with the data.
        iren.Initialize()
        renWin.Render()
        iren.Start()
        iren.show()

    def Surface(self):
        renWin = iren.GetRenderWindow()
        self.aRenderer = vtk.vtkRenderer()
        renWin.AddRenderer(self.aRenderer)
        self.v16 = vtk.vtkDICOMImageReader()
        self.v16.SetDirectoryName(self.dir)
        self.v16.Update()
        surfaceExtractor.SetInputConnection(self.v16.GetOutputPort())
        surfaceExtractor.SetValue(0, 500)
        surfaceNormals = vtk.vtkPolyDataNormals()
        surfaceNormals.SetInputConnection(surfaceExtractor.GetOutputPort())
        surfaceNormals.SetFeatureAngle(60.0)
        surfaceMapper = vtk.vtkPolyDataMapper()
        surfaceMapper.SetInputConnection(surfaceNormals.GetOutputPort())
        surfaceMapper.ScalarVisibilityOff()
        surface = vtk.vtkActor()
        surface.SetMapper(surfaceMapper)
        self.aRenderer.AddActor(surface)
        aCamera = vtk.vtkCamera()
        aCamera.SetViewUp(0, 0, -1)
        aCamera.SetPosition(0, 1, 0)
        aCamera.SetFocalPoint(0, 0, 0)
        aCamera.ComputeViewPlaneNormal()

        #self.aRenderer.AddActor(surface)
        self.aRenderer.SetActiveCamera(aCamera)
        self.aRenderer.ResetCamera()

        self.aRenderer.SetBackground(0, 0, 0)

        self.aRenderer.ResetCameraClippingRange()

        # Interact with the data.
        iren.Initialize()
        renWin.Render()
        iren.Start()
        iren.show()


app = QApplication(sys.argv)
# The class that connect Qt with VTK
iren = QVTKRenderWindowInteractor()
w = AppWindow()
#vtk_rendering()
w.show()
sys.exit(app.exec_())
# Start the event