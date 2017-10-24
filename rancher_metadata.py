from flask import Flask, Response
from urllib.request import urlopen

app = Flask(__name__)


def curl(url):
    return urlopen(url).read().decode()


def list_stacks():
    raw_stacks = curl("http://rancher-metadata/2015-12-19/stacks")
    return [g[1] for g in [f.split("=") for f in raw_stacks.split("\n") if len(f) > 0]]


def list_services(stack):
    raw_services = curl("http://rancher-metadata/2015-12-19/stacks/%s/services/" % stack)
    return [g[1] for g in [f.split("=") for f in raw_services.split("\n") if len(f) > 0]]


def service_create_index(stack, service):
    try:
        return int(curl("http://rancher-metadata/2015-12-19/stacks/%s/services/%s/create_index" % (stack, service)))
    except ValueError:
        return 0


@app.route("/metrics")
def stats():
    res = []
    stacks = list_stacks()
    # print("Stacks : %s" % stacks)
    for stack in stacks:
        services = list_services(stack)
        # print("Services for stack %s : %s" % (stack, services))
        for service in services:
            res.append("rancher_service_create_index{name=\"%s/%s\"} %s"
                       % (stack, service, service_create_index(stack, service)))
    return Response("%s\n" % "\n".join(res), mimetype='text/plain')

if __name__ == "__main__":
    app.run()
