import os
from pytubefix import YouTube
from pytubefix.cli import on_progress
#from moviepy.editor import VideoFileClip
import assemblyai as aai

def write_file(file_path, file_contents):
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)

    # Write the file to disk
    with open(file_path, "wb") as file:
        file.write(file_contents)

def transcribe_audio(file_path):
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file_path)

    if transcript.status == aai.TranscriptStatus.error:
        return transcript.error
    else:
        return transcript.text

def download_audio_from_youtube(youtube_url, output_file_name='audio'):
    try:
        yt = YouTube(youtube_url)
        print(yt.title)
        ys = yt.streams.get_audio_only()
        ys.download(filename=output_file_name, mp3=True)
    except Exception as e:
        raise Exception('Downloading video error: ', str(e))

    # try:
    #     video_clip = VideoFileClip(audio_file)
    #     video_clip.audio.write_audiofile(output_path)
    #     video_clip.close()
    # except Exception as e:
    #     raise Exception('Converting video error: ', str(e))
    return output_file_name+str('.mp3')