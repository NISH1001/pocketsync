# pocketsync
A naive data fetcher for pocket.

## Setup

- Setup virtual environment as `virtualenv venv/`
- Activate `source activate venv/bin/activate`
- Install [pockexport](https://github.com/karlicoss/pockexport)
- Install dependencies `pip install -r requirements.txt`
- Create directory `data/`

## Sync

First, create `secrets.py` file with `consumer_key` and `accesss_token` variable in the parent directory.  
See [here](https://github.com/karlicoss/pockexport#exporting) for further reference.


`sh sync.sh`

## Dump Annotations
`python annotations.py --datapath=<path to sync.json- --title="<title of the article>"`

If the sync is successful and you have the correct path and the relevant title, you might see the annotations at `data/annotations/<title>.txt`.
