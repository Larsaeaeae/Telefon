#Abhängigkeiten importieren
import pyaudio
import numpy as np
import RPi.GPIO as gpio
import time

#Variablen definieren
chunk=1024
startsignal = True
maxValue = 2**16

#Pins deklarieren
gpio.setmode(gpio.BOARD)
gpio.setup(11, gpio.OUT)
gpio.setup(37, gpio.OUT)
gpio.setup(36, gpio.OUT)
gpio.setup(33, gpio.OUT)

def vorwaerts(zeit):
    gpio.output(11, True)
    gpio.output(37, True)
    gpio.output(36, False)
    gpio.output(33, False)
    skip(zeit)

#Ersatzfunktion für sleep(), da sonst der Puffer von PyAudio überläuft
def skip(seconds):
    samples = int(seconds * 44100)
    count = 0
    while count < samples:
        stream.read(chunk)
        count += chunk
        time.sleep(0.01)

#PyAudio Objekt erstellen
p=pyaudio.PyAudio()

#PyAudio-Stream öffnen, hier wird die Anzahl an Kanälen (Channels=2), die Abtastrate (rate=44100), Ein- oder Ausgang (input=True),
#das Audiogerät (input_device_index=10), und die Anzahl an Frames im Buffer festegelegt (frames_per_buffer=1024)

stream=p.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True, input_device_index=10, frames_per_buffer=1024)
skip(0.5)
#solange ein gewisser Start-pegel nicht überschritten wird, warten wir
while (startsignal):
      #Mikrofonsignal einlesen
      data = np.frombuffer(stream.read(1024, exception_on_overflow = False),dtype=np.int16)
      #zwei-spaltiges Array data in die einzelnen Kanäle dataR und dataL aufteilen
      dataR = data[0::2]
      dataL = data[1::2]
      #Peak im Array pro Kanal finden
      peakL = np.abs(np.max(dataL)-np.min(dataL))/maxValue
      peakR = np.abs(np.max(dataR)-np.min(dataR))/maxValue
      #beide Peaks ausgeben
      print("L:%00.02f R:%00.02f"%(peakL*100, peakR*100))
      #wenn Signal laut genug, dann Startsignal auf False, damit losgefahren werden kann
      if ((peakL*100 > 5 or peakR*100 > 5)):
        startsignal=False
        #Durchschnitt des Peaks der beiden Kanäle berechnen, um später die Lautstärke vergleichen zu können 
        letzter_peak = (peakL*100+peakR*100)/2 
        print("Start!")
      else:
        #Signal zu leise
        print("noch kein Startsignal bekommen")
      skip(0.2)

#Schleife 250 Mal durchlaufen
for i in range(250):
    #festlegen, dass in diesem Schleifendurchlauf noch nicht gefahren wurde, um nicht in mehr als einen Case pro Schleifendurchlauf zu kommen. 
    bereits_gefahren=False
    #Mikrofonsignal einlesen
    data = np.frombuffer(stream.read(1024, exception_on_overflow = False),dtype=np.int16)
    #zwei-spaltiges Array data in die einzelnen Kanäle dataR und dataL aufteilen
    dataR = data[0::2]
    dataL = data[1::2]
    #Peak im Array pro Kanal finden
    peakL = np.abs(float(np.max(dataL))-float(np.min(dataL)))/maxValue
    peakR = np.abs(float(np.max(dataR))-float(np.min(dataR)))/maxValue
    #Pegeldifferenz zwischen links und rechts errechnen und ausgeben
    offset = (peakL-peakR)*10
    print("L:%00.02f R:%00.02f"%(peakL*100, peakR*100))
    #Wenn die Differenz der Pegel zu klein ist und das Singal laut genug ist, fahren wir geradeaus
    if (0.05 > offset and offset >-0.05 and ((peakL*100+peakR*100)/2) >2.8):
       #Durchschnitt des aktuellen Peaks der beiden Kanäle berechnen, um die Lautstärke vergleichen zu können 
       aktueller_peak = (peakL*100+peakR*100)/2 
       #wenn der aktuelle Peak kleiner ist als der letzte Peak, dann 1,5 Sekunden drehen
       if (aktueller_peak < letzter_peak):
            #Differenz berechnen, um diese ausgeben zu können
            differenz = letzter_peak-aktueller_peak
            #für den nächsten Schleifendurchlauf den aktuelllen Peak als letzten Peak setzen
            letzter_peak = aktueller_peak
            print("drehen Differeznz zum letzten Peak"+str(differenz))
            links(1.7)
       print("vorwaerts(0.8) "+str(offset))
       print(" ")
       vorwaerts(1.1)
       stop() 
       bereits_gefahren = True
       skip(0.1)

    #wenn die Pegeldifferenz größer als 0,05 ist und wir in diesem Schleifendurchlauf noch nicht gefahren sind, 0,5 Sekunden nach links drehen, anschließend 1,1 Sekunden geradeaus fahren
    if (offset>0.05 and not bereits_gefahren):
        #für den nächsten Schleifendurchlauf den aktuelllen Peak als letzten Peak setzen
        letzter_peak = (peakL*100+peakR*100)/2 
        print("links(0.8) "+str(offset))
        print(" ")
        links(0.55)
        #drehen anhalten, bevor wir beginnen geradeaus zu fahren
        stop()
        vorwaerts(1.1)
        #fertig für diesen Schleifendurchlauf, also anhalten
        stop() 
        #Schleifenabbruchbedingung setzen
        bereits_gefahren = True
        skip(0.1)

    #wenn die Pegeldifferenz kleiner als -0,05 ist und wir in diesem Schleifendurchlauf noch nicht gefahren sind, 0,5 Sekunden nach rechts drehen, anschließend 1,1 Sekunden geradeaus fahren
    if (offset<-0.05 and not bereits_gefahren):
        #für den nächsten Schleifendurchlauf den aktuelllen Peak als letzten Peak setzen
        letzter_peak = (peakL*100+peakR*100)/2
        print("rechts(0.8) "+str(offset))
        print(" ")
        rechts(0.55)
        #drehen anhalten, bevor wir beginnen geradeaus zu fahren
        stop()
        vorwaerts(1.1)
        #fertig für diesen Schleifendurchlauf, also anhalten
        stop()
        #Schleifenabbruchbedingung setzen
        bereits_gefahren = True
        skip(0.1)
    #wenn das Signal zu leise sind und wir noch nicht gefahren sind, ausgeben das wir warten und 0.25 Sekunden warten 
    if (peakL+peakR/2 < 10 and not bereits_gefahren):
        print("warte weil ruhig")
        print(" ")
        bereits_gefahren = True
        skip(0.25)
#250 Schleifendurchläufe erreicht, Auto anhalten, GPIOs wieder freigeben, Stream schließen und das PyAudio-Objekt terminieren
stop()
gpio.cleanup()
stream.close
p.terminate