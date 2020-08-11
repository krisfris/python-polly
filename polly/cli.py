import click

import polly.client


@click.group()
def cli():
    pass


@cli.command()
def server():
    import polly.server
    polly.server.run_server('localhost', 6000)


@cli.command()
@click.argument('text')
@click.option('--queue/--no-queue', default=True)
def say(text, queue):
    polly.client.say(text, queue=queue)


if __name__ == '__main__':
    cli()
