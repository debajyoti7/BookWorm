#!/usr/bin/python
#-*- coding:utf8 -*-
#This code was originally intended by Debayan (debayanin@gmail.com) to generate the training files for tesseract-ocr for bootstrapping a new character set
#but this somewhat modified version is being used only to generate the individual characters, i.e., only sayamindu's code is critical here
#However, Debayan's work has been a true source of guidance, and I hereby acknowledge it. Also included is his original README file.

import file
import train

import os
import sys

#Sayamindu's code
import cairo
import pango
import pangocairo

import ImageFont, ImageDraw, ImageChops
from PIL import Image


bigbox=()

def expand(temp_bbox):
    """expand a bounding box a little bit"""
    tol=2
    bbox=(temp_bbox[0]-tol,temp_bbox[1]-tol,temp_bbox[2]+tol,temp_bbox[3]+tol)
    return bbox


def draw(font_string,font_size,lang,alphabets,outdir="."): # language, font file name, font full path, font size, characters
    """ Generates tif images and box files"""
    
    
    image_dir=lang+"."+"images"
    if(os.path.exists(image_dir)):
        pass
    else:
        os.mkdir(image_dir)
       
    #Using a font
    #font= ImageFont.truetype(font,fsz)
    boxfile=image_dir+"/"+"bigimage.box"
    f=open(boxfile,"w")
    wt = 4000
    ht = 4000 #modified later using a separate script
	
    bigimage=Image.new("L",(wt,ht),255)	#change here for inverting
    bigdraw=ImageDraw.Draw(bigimage)
    x=y=10
    count=0
    for akshar in alphabets:
        akshar.strip() #remove nasty characters
       
        #I shall now create an image with black bgc and white font color. One
        #getbbox() determines the bounding box values I shall invert the image.
        #This has to be done since getbbox() only finds bounding box values for
        #non-zero pixels (read as white), but tesseract-ocr runs on the exact
        #opposite bgc fgc combination. Contact debayanin@gmail.com.
      
       
        #The lines below are pango/cairo code 
        surface = cairo.ImageSurface(cairo.FORMAT_A8, font_size*4, font_size*3)
        context = cairo.Context(surface)

        pc = pangocairo.CairoContext(context)

        layout = pc.create_layout()
        layout.set_font_description(pango.FontDescription(font_string))
        layout.set_text(akshar)
        print akshar

        #  lines take care of centering the text.
        width, height = surface.get_width(), surface.get_height()
        w, h = layout.get_pixel_size()
        position = (10,10) #most likely this part messes up when you try to change the size within this script. It is suggested to use the separate script.
        context.move_to(*position)
        pc.show_layout(layout)
        surface.write_to_png("pango.png")
	
        #Here we open the generated image using PIL functions
        temp_image=Image.open("pango.png") #black background, white text
        draw = ImageDraw.Draw(temp_image)
        bbox = temp_image.getbbox()
        deltax=bbox[2]-bbox[0]
        deltay=bbox[3]-bbox[1]

       
        print bbox
        new_image=temp_image.crop(bbox)
        temp_image=temp_image.load()
        inverted_image = ImageChops.invert(new_image) #White background, black text
	
	inverted_image.save(image_dir+"/"+str(count)+".png")
	bigimage.paste(inverted_image,(x,y))
	os.unlink(image_dir+"/"+str(count)+".png")
	count = count+1
	#bigimage.load()
        bigbox=(x,y,x+deltax,y+deltay)
        print bigbox
        draw=ImageDraw.Draw(bigimage)
	#draw.rectangle(bigbox,None,100)
        x=bigbox[2]+5
        if x>(wt-10):
            x=10; y=y+40

        os.unlink("pango.png") #delete the pango generated png

        line=akshar+" "+str(bigbox[0]-1)+" "+str(ht-(bigbox[1]+deltay)-1)+" "+str(bigbox[2]+1)+" "+str(ht-(bigbox[3]-deltay)+1) # this is the line to be added to the box file
	f.write(line+'\n')

	#degrade code starts
	strip=[deltax*.2,deltax*.4,deltax*.7]
	for values in range(0,2):
		distort2=inverted_image
		for wai in range(0,deltay):
			for ex in range(strip[values],strip[values]+1):
				distort2.putpixel((ex,wai),255)
		bigbox=(x,y,x+deltax,y+deltay)
		#draw.rectangle(bigbox,None,10)
		line=akshar+" "+str(bigbox[0]-1)+" "+str(ht-(bigbox[1]+deltay)-1)+" "+str(bigbox[2]+1)+" "+str(ht-(bigbox[3]-deltay)+1) # this is the line to be added to the box file
        	f.write(line+'\n')
		bigimage.paste(distort2,(x,y))
		x=bigbox[2]+5
        	if x>(wt-10):
            		x=10; y=y+40
		
			
	#degrade code ends
     
        #distort.distort(filename2,bbox,fsz,akshar)
     
       
       
    #bigimage.save(image_dir+"/"+"bigimage.tif","TIFF") #useful to generate merged file for all images when using default sizes.
    f.close()
    train.train(lang,outdir)
       
if __name__ == "__main__":           
	if(len(sys.argv)!=9):
	    print "Usage: python generate.py -font <font name> -l <language> -s <size> -a <input alphabet directory>"
	    exit()
	
	if(sys.argv[1]=="-font"):
	    font_name=sys.argv[2]
	else:
	    print "Usage: python generate.py -font <font name> -l <language> -s <size> -a <input alphabet directory>"
	    exit()
	       
	if(sys.argv[3]=="-l"):
	    lang=sys.argv[4]
	else:
	    print "Usage: python generate.py -font <font name> -l <language> -s <size> -a <input alphabet directory>"
	    exit()
	   
	if(sys.argv[5]=="-s"):
	    font_size=sys.argv[6]
	else:
	    print "Usage: python generate.py -font <font name> -l <language> -s <size> -a <input alphabet directory>"
	    exit()
	
	if(sys.argv[7]=="-a"):
	    alphabet_dir=sys.argv[8]
	else:
	    print "Usage: python generate.py -font <font name> -l <language> -s <size> -a <input alphabet directory>"
	    exit()
	
	font_string=font_name+" "+lang+" "+font_size


	#begin training    
	draw(font_string,int(font_size),lang,file.read_file(alphabet_dir))#reads all fonts in the directory font_dir and trains




