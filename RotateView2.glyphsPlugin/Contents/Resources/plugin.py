# encoding: utf-8
from __future__ import division, print_function, unicode_literals

###########################################################################################################
#
#
#	General Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/General%20Plugin
#
#
###########################################################################################################


#https://developer.apple.com/library/content/documentation/Cocoa/Conceptual/CocoaViewsGuide/SubclassingNSView/SubclassingNSView.html

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from vanilla import VanillaBaseObject
from AppKit import NSAffineTransform, NSAffineTransformStruct, NSRectFill, NSView, NSNoBorder, NSColor, NSBezierPath, NSFullSizeContentViewWindowMask
from Foundation import NSWidth, NSHeight, NSMidX, NSMidY
import traceback, math

## Viewer class that contains the copied glyph
#------------------------

class RotatePreviewView(NSView):
	def drawRect_(self, rect):
		def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
			myTransform = NSAffineTransform.transform()
			if rotate:
				myTransform.rotateByDegrees_(rotate)
			if scale != 1.0:
				myTransform.scaleBy_(scale)
			if not (shiftX == 0.0 and shiftY == 0.0):
				myTransform.translateXBy_yBy_(shiftX,shiftY)
			if skew:
				myTransform.shearBy_(math.tan(math.radians(skew)))
			return myTransform
		
		NSColor.whiteColor().set()
		NSBezierPath.fillRect_(rect)

		if Glyphs.font is None or not Glyphs.font.currentTab:
			return
		
		if not Glyphs.font.currentTab.layers:
			return
		
		try:
			previewPath = NSBezierPath.bezierPath()
			for layer in Glyphs.font.currentTab.layers:
				if type(layer) == GSControlLayer:
					break
				previewPath.appendBezierPath_(layer.bezierPath)
				previewPath.transformUsingAffineTransform_(
					transform(shiftX=-layer.width),
				)
				
			rotationFactor = Glyphs.defaults['com.saja.RotateView2.angle']
			Width = NSWidth(self.frame())
			Height = NSHeight(self.frame())
			scaleFactor = 0.666666 / (Glyphs.font.upm / min(Width, Height))
			
			## scaling and zeroing the glyph
			bounds = previewPath.bounds()
			previewPath.transformUsingAffineTransform_( 
				transform(
					scale=scaleFactor,
					shiftX=-NSMidX(bounds),
					shiftY=-NSMidY(bounds),
				) 
			)
			
			## rotation
			previewPath.transformUsingAffineTransform_( 
				transform(
					rotate=rotationFactor,
				)
			)
			
			## positioning to the middle of the viewport
			previewPath.transformUsingAffineTransform_(
				transform(
					shiftX=Width / 2,
					shiftY=Height / 2 - 8,
				)
			)
	
			## fill path
			NSColor.blackColor().set()
			previewPath.fill()
		except:
			print(traceback.format_exc())


class RotatePreview(VanillaBaseObject):
	nsGlyphPreviewClass = RotatePreviewView
	
	@objc.python_method
	def __init__(self, posSize):
		if Glyphs.defaults['com.saja.RotateView2.angle'] is None:
			Glyphs.defaults['com.saja.RotateView2.angle'] = 0.0
		self._setupView(self.nsGlyphPreviewClass, posSize)
		self._nsObject.wrapper = self
	
	@objc.python_method
	def redraw(self):
		self._nsObject.setNeedsDisplay_(True)


class RotateView2(GeneralPlugin):
	@objc.python_method
	def settings(self):
		self.name = "Rotate View 2"


	@objc.python_method
	def start(self):
		newMenuItem = NSMenuItem(self.name, self.showWindow_)
		Glyphs.menu[WINDOW_MENU].append(newMenuItem)
		
		# Set default value
		Glyphs.registerDefault('com.saja.RotateView2.angle', 0.0)


	def showWindow_(self, sender):
		try:
			from vanilla import Group, Slider, TextBox, Window
			self.windowWidth = 300
			self.windowHeight = 240
			
			self.w = Window((self.windowWidth, self.windowWidth), "Rotate View 2", minSize=(self.windowWidth, self.windowWidth), autosaveName="com.saja.RotateView2.window")
			window = self.w.getNSWindow()
			window.setStyleMask_(window.styleMask() | NSFullSizeContentViewWindowMask)
			try:# only available in 10.10
				window.setTitlebarAppearsTransparent_(True)
			except:
				pass
			#window.toolbar = nil;
			window.setMovableByWindowBackground_(True)
			
			currentRotation = Glyphs.defaults['com.saja.RotateView2.angle']
			if currentRotation is None:
				currentRotation = 0.0
			
			self.w.Preview = RotatePreview((0, 0, -0, -28))
			self.w.controlBox = Group((0, -28, -0, -0))
			self.w.controlBox.slider = Slider((10, 2, -55, 28), tickMarkCount=9, callback=self.sliderCallback, value=currentRotation, minValue=-180, maxValue=180)
			self.w.controlBox.textBox = TextBox( (-55, -23, -5, -3), text=f"{int(currentRotation)}°", alignment="center")
			# self.w.controlBox.slider.getNSSlider().setEnabled_(False)
		
			self.w.open()
			self.changeGlyph_(None)
			Glyphs.addCallback( self.changeGlyph_, UPDATEINTERFACE ) #will be called on ever change to the interface
		except:
			print(traceback.format_exc())

	@objc.python_method
	def __del__(self):
		Glyphs.removeCallback( self.changeGlyph_, UPDATEINTERFACE )

	
	@objc.python_method
	def sliderCallback(self, sender):
		currentValue = '{:.0f}'.format(sender.get())
		self.w.controlBox.textBox.set(str(currentValue)+"°")
		Glyphs.defaults['com.saja.RotateView2.angle'] = float(currentValue)
		self.w.Preview.redraw()


	## on Glyph Change, update the viewer
	#------------------------------
	
	def changeGlyph_(self, sender):
		# self.w.controlBox.slider.getNSSlider().setEnabled_(Glyphs.font and Glyphs.font.selectedLayers)
		self.w.Preview.redraw()

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
