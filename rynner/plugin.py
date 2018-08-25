from rynner.run import Run


class RunAction:
    def __init__(self, label, function):
        self.label = label
        self.function = function


class Plugin:
    '''
    The runner object (function) it the thing that is responsible for running
    the job, usually by creating a Run object.
    Links the GUI/UI and the 'run' logic.
    (see design.org example)
    '''

    build_index_view = None

    view_keys = ("id", "name")

    def __init__(self,
                 domain,
                 name,
                 create_view=None,
                 runner=None,
                 view_keys=None,
                 labels=None,
                 build_index_view=None):
        '''
        domain: a string giving a globally unique name for the plugin. Clients on different machines will use this name to associate jobs with a given Plugin class. The recommended appraoach is to use a web URL (such as a github repository URL) which is unique for this plugin. This string is never displayed in the UI by default.
        name: a string giving the human readable Plugin name. This is the string which is displayed to the user in the UI to identify the runs of this plugin.
        create_view : an instance of RynCreateView, which defines the view used by the application user to configure a job, and the mapping of that configuration to a set of options which will be passed to Run
        runner: a function which will be called to run a job. Typically this function will instantiate one or more objects of type Run. The input to the method will be a dictionary in which the keys correspond to the 'key' properties of the visible UI objects in the . See the RynCreateView class documentation for details of keys. If not specified, all keys of the RynCreateView object will be passed as keyword arguments to instantiate a single Run object. In this case, the keys of the children of the RynCreateView should correspond directly to keyword arguments of Run.
        view_keys: iterable of strings giving a list of keys to show in the (default) main/index view
        labels: (optional) dictionary giving a human readable name for each label. If not specified, the values of the key of each entry in  is used.
        view: a callable that when called returns a QWidget object (this should be a QWidget class or a function which returns a QWidget instance). If not set, RynCreateView will be used. view keyword argument which can be used to override the default main/index view to render for a Plugin.
        '''
        self.name = name
        self.domain = domain
        self.create_view = create_view
        self.actions = []
        self.runner = runner
        self.labels = labels

        if build_index_view is not None:
            self.build_index_view = build_index_view

        if view_keys is not None:
            self.view_keys = view_keys

    def create(self):
        if self.create_view is None:
            self._run({})
        else:
            # display configuration window
            accepted = self.create_view.exec_()

            if accepted and len(self.create_view.invalid()) == 0:
                data = self.create_view.data()
                self._run(data)

    def _run(self, data):
        if self.runner is None:
            run = Run(**data)
        else:
            self.runner(data)

    def add_action(self, label, function):
        action = RunAction(label, function)
        self.actions.append(action)
        return action

    def list_jobs(self, hosts):
        jobs = []
        for host in hosts:
            for job in host.jobs(self.domain):
                jobs.append(job)
        return jobs


class PluginCollection:
    '''
    This class allows a collection of Plugin objects to be used with the same API as a single object.
    '''

    build_index_view = None

    def __init__(self, name, plugins, view_keys=None, labels=None):
        self.name = name
        self.plugins = plugins
        if view_keys is None:
            self.view_keys = Plugin.view_keys
        else:
            self.view_keys = view_keys

        self.actions = []

        self.labels = labels
        self.create_view = None

    def list_jobs(self, hosts):
        jobs = [
            job for host in hosts for plugin in self.plugins
            for job in host.jobs(plugin.domain)
        ]
        return jobs