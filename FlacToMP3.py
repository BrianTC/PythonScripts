#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import os.path
import sys
import threading 
import math
LAME_CAN_DECODE_FLAC=0
MAX_THREADS=10
PRINT_DEBUG_INFO=0
def escapeStr(istr):
	escapeList=' "()&\'~-![].'
	for i in range( len(escapeList) ):
		istr=istr.replace(escapeList[i],'\\'+escapeList[i])
	return istr
def escapeQuotes(istr):
	return istr.replace('"','\\"')
def getFLACTag(ffile,tag):
	ffile=os.path.abspath(ffile)
	if(not os.path.exists(ffile) or not os.path.isfile(ffile)):
		return ''
	ffile=escapeStr(ffile)#now it needs to be escaped so the actual shell command can be run on it
	f=os.popen('metaflac --show-tag=%s %s'%(tag,ffile))
	flacInfo=f.read()
	f.close()
	result=flacInfo[flacInfo.find('=')+1:].strip()
	return escapeQuotes(result)
def aArtExport(ffile):
	coverName="python_cover.jpg"
	ffile=os.path.abspath(ffile)
	dname=os.path.dirname(ffile)
	exportCmd="metaflac --export-picture-to=%s/%s %s"%(escapeStr(dname),escapeStr(coverName),escapeStr(ffile))
	os.system(exportCmd)
	return dname+'/'+coverName

def convertFile(ffile,base_change=''):
	fileBase,ext=os.path.splitext(ffile)
	mp3File=fileBase+'.mp3'
	#tagging ref: http://age.hobba.nl/audio/tag_frame_reference.html
	#see also http://id3.org/id3v2.4.0-frames
	#and http://lame.cvs.sourceforge.net/viewvc/lame/lame/doc/html/detailed.html#tv
	title=getFLACTag(ffile,'TITLE')
	year=getFLACTag(ffile,'DATE')
	artist=getFLACTag(ffile,'ARTIST')
	aartist=getFLACTag(ffile,'ALBUMARTIST')
	composer=getFLACTag(ffile,'COMPOSER')
	album=getFLACTag(ffile,'ALBUM')
	comment=getFLACTag(ffile,'COMMENT')
	genre=getFLACTag(ffile,'GENRE')
	track=getFLACTag(ffile,'TRACKNUMBER')
	totalTracks=getFLACTag(ffile,'TRACKTOTAL')
	if totalTracks=='' :
		totalTracks=getFLACTag(ffile,'TOTALTRACKS')
	discNo=getFLACTag(ffile,'DISCNUMBER')
	discTotal=getFLACTag(ffile,'DISCTOTAL')
	if discTotal=='':
		discTotal=getFLACTag(ffile,'TOTALDISCS')
	isrc=getFLACTag(ffile,'ISRC')
	#end tags so to say

	# print(title)
	# print(year)
	# print(artist)
	# print(aartist)
	# print(composer)
	# print(album)
	# print(comment)
	# print(genre)
	# print(track)
	# print(totalTracks)
	# print(discNo)
	# print(discTotal)
	# print(cover)
	#album art:
	cover=aArtExport(ffile)
	if os.path.isfile(cover):
		cover = '--ti "%s"'%cover
	else:
		cover=''
	#base command
	command='lame --preset insane --id3v2-only --id3v2-utf16 --tt "%s" --ta "%s" --tl "%s" --ty "%s" --tn %s/%s --tc "%s" --tg "%s" --tv "TPOS=%s/%s" --tv "TCOM=%s" --tv "TSRC=%s" --tv "TPE2=%s" %s'\
		% (title, artist, album, year, track,totalTracks,comment,genre,discNo,discTotal,composer,isrc,aartist,cover)
	#-----------------------------
	#for when lame can decode FLAC
	if LAME_CAN_DECODE_FLAC == 1 :
		command = command+' %s %s'
		command=command% (escapeStr(ffile), escapeStr(mp3File))
		#ommand=command%(ffile,mp3file)
	#-----------------------------
	#for when it can't decode flac
	else:
		#command = 'flac --decode --stdout %s |'+command+' - %s'
		#command=command% (escapeStr(ffile), escapeStr(mp3File))
		command = 'flac --decode --stdout "%s" |'+command+' - "%s"'
		command=command%(ffile,mp3File)
	#print(ffile.encode())
	if(PRINT_DEBUG_INFO):
		print(command.encode('ascii','ignore'))
	os.system(command)
def convertDirectory(files):
	print(len(files))
	for file in files:
		try:
			convertFile(file)
		except(UnicodeEncodeError,UnicodeDecodeError):
			pass
def multiThread(files):
	#how many threads to use?
	ttu=min(MAX_THREADS,len(files))
	filesPerThread=math.ceil(len(files)/ttu)
	threads=[]
	for i in range(ttu):
		sidx=i*filesPerThread
		eidx=min(sidx+filesPerThread,len(files))
		# print(sidx)
		# print(eidx)
		# print(files[sidx:eidx])
		arglist=[]+files[sidx:eidx]
		t=threading.Thread(target=convertDirectory,args=[arglist])
		t.start()
		threads.append(t)



multiThread(sys.argv[1:])
