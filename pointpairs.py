'''
* Copyright 2015-2017 European Atomic Energy Community (EURATOM)
*
* Licensed under the EUPL, Version 1.1 or - as soon they
  will be approved by the European Commission - subsequent
  versions of the EUPL (the "Licence");
* You may not use this work except in compliance with the
  Licence.
* You may obtain a copy of the Licence at:
*
* https://joinup.ec.europa.eu/software/page/eupl
*
* Unless required by applicable law or agreed to in
  writing, software distributed under the Licence is
  distributed on an "AS IS" basis,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
  express or implied.
* See the Licence for the specific language governing
  permissions and limitations under the Licence.
'''


"""
Class for storing 'point pairs': coordinate of matching points
on 2D camera images and 3D CAD models.

Written by Scott Silburn (scott.silburn@ukaea.uk)
"""
 
import vtk
import numpy as np
import os
import paths
import csv
import image
import sys


# Simple class for storing results.
class PointPairs():
    
	def __init__(self,loadname=None,image=None):
		self.imagepoints = []
		self.objectpoints = []
		self.machine_name = None
		self.name = None
		self.image = None

		if loadname is not None:
			self.load(loadname)
		if self.image is None and image is not None:
			self.set_image(image)

	def set_image(self,image):
		self.image = image
		self.n_fields = image.n_fields


	# Save point pairs to csv file
	def save(self,savename):

		# Make sure we have a copy of the image being used saved.
		if self.image.name is None:
				self.image.name = savename
    
		self.image.save()

		# Set the point pair set name to the save name
		self.name = savename

		savefile = open(os.path.join(paths.pointpairs,self.name + '.csv'),'wb')

		csvwriter = csv.writer(savefile)
		header = []
		header.append(['CalCam Point Pairs File'])
		header.append(['Machine:',self.machine_name])
		header.append(['Image:',self.image.name])
		header.append(['','',''])
		header.append(["Machine X","Machine Y","Machine Z"])
		for i in range(self.image.n_fields):
				header[3] = header[3] + ['',"Field " + str(i),'']
				header[4] = header[4] + ['',"Image X","Image Y"]

		for headrow in header:			
				csvwriter.writerow(headrow)

		for i in range(len(self.objectpoints)):
				row = [self.objectpoints[i][0],self.objectpoints[i][1],self.objectpoints[i][2]]
				for j in range(self.image.n_fields):
					if self.imagepoints[i][j] is None:
						row = row + ['','','']
					else:
						row = row + [''] + list(self.imagepoints[i][j])

				csvwriter.writerow(row)

		savefile.close()

	def load(self,savename):

		savefile = open(os.path.join(paths.pointpairs,savename + '.csv'),'r')

		csvreader = csv.reader(savefile)

		# Read header info...
		headrow = [None]
		while headrow[0] != 'Machine X':
				# Get the next header line
				headrow = next(csvreader)
				if headrow[0] == 'Machine:':
					self.machine_name = headrow[1]
				elif headrow[0] == 'Image:' and self.image is None:
					try:
						self.image = image.Image(headrow[1])
					except:
						print('[calcam.PointPairs] Cannot load image "' + headrow[1] + '" for these point pairs: ' + sys.exc_info()[1].__str__())
						self.image = None

				elif headrow[0] == 'Machine X':
					self.n_fields = int(np.floor( (len(headrow) - 4) / 2.))


		# Actually read the point pairs
		self.imagepoints = []
		self.objectpoints = []
        
		for row in csvreader:
				self.objectpoints.append((float(row[0]),float(row[1]),float(row[2])))
				self.imagepoints.append([])
				for field in range(self.n_fields):
					if row[1 + (field+1)*3] != '':
						self.imagepoints[-1].append( [float(row[1 + (field+1)*3]) , float(row[2 + (field+1)*3])] )
					else:
						self.imagepoints[-1].append(None)

		self.name = savename

		savefile.close()
