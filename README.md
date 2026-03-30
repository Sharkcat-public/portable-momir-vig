# portable-momir-vig

## Setup of Raspberry Pi
`curl -LsSf https://astral.sh/uv/install.sh | sh`

## First time setup of project
`uv venv --system-site-packages`<br>
`uv sync`<br>
`source .venv/bin/activate`<br>
`python setup.py`<br>

## Setup to start on boot
`sudo nano /lib/systemd/system/momir-vig.service`<br>

	[Unit]
	Description=Momir Vig portable generator
	After=boot-complete.target
	
	[Service]
	ExecStart=/bin/bash -c '/home/sharkcat/Documents/portable-momir-vig/.venv/bin/python /home/sharkcat/Documents/portable-momir-vig/main.py >> /home/sharkcat/Documents/portable-momir-vig/log.log 2>&1'
	
	[Install]
	WantedBy=boot-complete.target

`sudo systemctl daemon-reload`<br>
`sudo systemctl enable momir-vig.service`<br>
