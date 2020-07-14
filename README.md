<p align="center">
  <img src="screenshots/logo-horuz.png"/>
</p>

Horuz!. CLI to interact with ElasticSearch. Keep an eye of your Fuzzing!

Installing
----------
**ElasticSearch**

https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html


**Pip**

```console
$ sudo apt-get update

$ sudo apt-get -y install python3-pip
```

**Horuz**

```console
$ git clone git@github.com:misalabs/horuz.git

$ cd horuz

$ pip3 install --editable .
```

Usage
-----

```console
$ hz --help

$ hz config server:status
ElasticSearch is connected to http://localhost:9200 successfully!
```

Collect data examples
---------------------
##### Using ffuf

Custom integration with ffuf.

```console
$ hz collect -p x.com -c "ffuf -w ~/SecLists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ"
```
![](screenshots/screenshot1.gif)

##### Custom JSON files

In this example, we have an httprobe.txt file, then it will be transformed to JSON file.

```
$ cat httprobe.txt | jq -Rnc '[inputs|split("\n")|{("host"):.[0]}]' > httprobe.json
```

Then, upload it to ES.

```
$ hz collect -p att_probe_ex -f httprobe.json
⠦ Collecting...
Session name: gallant_satoshi_8455236

Results: 1366

$ hz search -p att_probe_ex -q "session:gallant_satoshi_8455236" -oJ -f time,host -s 2
[   
    {   
        "host": "https://atracciondetalento.att.com.mx",
        "time": "2020-07-14T20:35:04.668051"
    },
    {   
        "host": "https://foro.att.com.mx",
        "time": "2020-07-14T20:35:04.663304"
    }
]

```




Query search examples
--------------

Search by range dates:

```console
$ hz search -p x.com -q "time:[2020-04-15 TO 2020-05-20]"
```

Search by wildcard in the field

```console
$ hz search -p x.com -q "result.html:*key*" -oJ -f html
```
![](screenshots/screenshots4.gif)

Pipe the result to other commands

```console
$ hz search -p yahoo.com -q "session:*" -oJ -f _id,session,time | jq ".[].session" | sort -
```
![](screenshots/screenshots6.gif)
