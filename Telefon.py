#Import libraries
import pyaudio
import wave
import RPi.GPIO as gpio

#Declare raspberry pi hardware pins
gpio.setmode(gpio.BOARD)
gpio.setup(16, gpio.IN)

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 44100  # Record at 44100 samples per second
seconds = 3
filename = "Test.wav"

RecordingCounter = 0

while(True):


    # Start playing intro sound if handset picked up
    if (not WelcomeDone and not gpio.input(16)):

        print('Playing Welcome Message')

        filename = 'Welcome.wav'

        # Set chunk size of 1024 samples per data frame
        chunk = 1024  

        # Open the sound file 
        wf = wave.open(filename, 'rb')

        # Create an interface to PortAudio
        p = pyaudio.PyAudio()

        # Open a .Stream object to write the WAV file to
        # 'output = True' indicates that the sound will be played rather than recorded
        stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = wf.getframerate(),
                        output = True)

        # Read data in chunks
        data = wf.readframes(chunk)

        # Play the sound by writing the audio data to the stream
        while (data != b''):
            stream.write(data)
            data = wf.readframes(chunk)
            print(data)

        # Close and terminate the stream
        stream.close()
        p.terminate()


        print('Playing Welcome Message Completed')


    # Start Recording user message
        RecordingCounter = RecordingCounter + 1

        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 2
        fs = 44100  # Record at 44100 samples per second
        seconds = 3
        filename = "Recording" + str(RecordingCounter) + ".wav"

        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        print('Recording')

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

        frames = []  # Initialize array to store frames

        # Stop recording if handset on-hook
        while (not gpio.input(16)):
            data = stream.read(chunk)
            frames.append(data)

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()

        print('Finished recording')

        # Save the recorded data as a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()
