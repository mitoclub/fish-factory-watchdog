# Fish factory watchdog

Scripts for remote aquarium sensors information collection

## How to run watchdog

1. Run script [app.py](./app.py) on 'locally' remote server
2. Run script [ZebraFishMaster.py](./ZebraFishMaster.py) on fish-factory laptope

## How it works

- [app.py](./app.py) listens network and wait POST request from client app
- client app [ZebraFishMaster.py](./ZebraFishMaster.py) send log files through POST request to server
- when server got file, it run script [bot.py](./bot.py) that read stdin and send messages to discord

## Plan

1. set up logging for main script (done)
2. repair heating and signal system (drop inadequate values from samples)
3. write script that will periodically send logs to discord channel (done)
4. set up connection factory-server-channel through ssh (done)
