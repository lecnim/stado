class Deployer:
    pass

class GenericDeployer(Deployer):

    def deploy(self, path, source):

        with open(path) as file:
            file.write(source)