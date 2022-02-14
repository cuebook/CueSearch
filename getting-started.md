# Getting Started

## Install via Docker-Compose

```
mkdir -p ~/cuebook
wget https://raw.githubusercontent.com/cuebook/CueSearch/main/docker-compose-prod.yml -q -O ~/cuebook/docker-compose-prod.yml
wget https://raw.githubusercontent.com/cuebook/CueSearch/main/.env -q -O ~/cuebook/.env
cd ~/cuebook
```

```
docker-compose -f docker-compose-prod.yml --env-file .env up -d
```



## Add Connection

Go to the Connections screen to create a connection.

![](.gitbook/assets/Add\_connection.png)

## Add Dataset

Next, create a dataset using your connection. See [Datasets](datasets.md) for details.

## Card Template

To add, update or delete a template visit [Card Templates](card-templates.md) section.

## Indexing

* Hourly indexing job is running every hour.
* For instant indexing run via api  [http://localhost:3000/api/cueSearch/runIndexing/](http://localhost:3000/api/cueSearch/runIndexing/).
* Action with global dimension starts indexing job.

## Search Results

Write filter in search bar and then select from dropdown and press search icon.

![Search Result](.gitbook/assets/Search\_results.png)

