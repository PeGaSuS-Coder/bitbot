import signal
from src import Config, ModuleManager, utils

class Module(ModuleManager.BaseModule):
    def on_load(self):
        self._exited = False
        signal.signal(signal.SIGINT, self.SIGINT)
        signal.signal(signal.SIGUSR1, self.SIGUSR1)

    def SIGINT(self, signum, frame):
        print()
        self.bot.trigger(lambda: self._kill(signum))

    def _kill(self, signum):
        if self._exited:
            return
        self._exited = True

        self.events.on("signal.interrupt").call(signum=signum)

        for server in self.bot.servers.values():
            server.socket.clear_send_buffer()
            line = server.send_quit("Shutting down")
            server.send_enabled = False
            line.on_send(self._make_hook(server))

    def _make_hook(self, server):
        return lambda: self.bot.disconnect(server)

    def SIGUSR1(self, signum, frame):
        self.bot.trigger(self._reload_config)

    def _reload_config(self):
        self.bot.log.info("Reloading config file", [])
        self.bot.config.load()
        self.bot.log.info("Reloaded config file", [])
