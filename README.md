# LLM-powered Drone Companion for Blind and Low Vision People


Code for the paper (still uner review)

## Hardware and Software: 
- Tello Drone (https://www.ryzerobotics.com/tello)
- Windows Laptop (Mac probably works just fine, but we recommend Windows.)
- WiFi Adapter
- Noise Cancelling Headphone with a mic
- Python version < 3.13 (We run it in 3.9.13) 

## Environment Set-up: 
Download Microsoft C++ Build Tools (https://visualstudio.microsoft.com/visual-cpp-build-tools/) 

Clone repo, create a new environment, and download the dependencies: 
```
git clone [xxx]
cd xxx
[create a new environment]
pip install -r requirements.txt
```

Check if ffmpeg (which is required to handle audio) exist:
```
ffmpeg -version
```
If the above command is not recognized, then this package is probably missing. To install ffmpeg, the easiest way being:

```
winget ffmpeg
```


## Run the demo:

## Final thoughts and other resources:
