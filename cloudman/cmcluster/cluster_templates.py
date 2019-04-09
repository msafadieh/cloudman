import abc
import os
import yaml
from rest_framework.exceptions import ValidationError
from .rancher import RancherClient
import subprocess


class CMClusterTemplate(object):

    def __init__(self, context, cluster):
        self.context = context
        self.cluster = cluster

    @property
    def connection_settings(self):
        return self.cluster.connection_settings

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def add_node(self, name, size):
        pass

    @abc.abstractmethod
    def remove_node(self):
        pass

    @abc.abstractmethod
    def activate_autoscaling(self, min_nodes=0, max_nodes=None, size=None):
        pass

    @abc.abstractmethod
    def deactivate_autoscaling(self):
        pass

    @staticmethod
    def get_template_for(context, cluster):
        if cluster.cluster_type == "KUBE_RANCHER":
            return CMRancherTemplate(context, cluster)
        else:
            raise KeyError("Cannon get cluster template for unknown cluster "
                           "type: %s" % cluster.cluster_type)


class CMRancherTemplate(CMClusterTemplate):

    def __init__(self, context, cluster):
        super(CMRancherTemplate, self).__init__(context, cluster)
        settings = cluster.connection_settings
        self._rancher_url = settings.get('rancher_url')
        self._rancher_api_key = settings.get('rancher_api_key')
        self._rancher_cluster_id = settings.get('rancher_cluster_id')
        self._rancher_project_id = settings.get('rancher_project_id')

    def setup(self):
        """
        Sets up the required environment for this template
        """
        self.fetch_kube_config()

    def fetch_kube_config(self):
        kube_config = self.rancher_client.fetch_kube_config()
        os.makedirs(os.path.expanduser("~/.kube/"), exist_ok=True)

        cfg_path = os.path.expanduser('~/.kube/config')
        new_cfg_path = f"{cfg_path}_{self.rancher_cluster_id}"
        with open(new_cfg_path, "w") as f:
            f.write(kube_config)
        # Activate the new cluster's context
        current_context = yaml.load(kube_config).get('current-context')
        # If an existing config is present, merge download config into it.
        # based on: https://github.com/kubernetes/kubernetes/issues/46381
        merge_cmd = (f"KUBECONFIG={cfg_path}:{new_cfg_path} kubectl config"
                     f" view --flatten > {new_cfg_path}_merged &&"
                     f" mv {new_cfg_path}_merged {cfg_path} &&"
                     f" rm {new_cfg_path} &&"
                     f" kubectl config use-context {current_context}")
        subprocess.check_output(merge_cmd, shell=True)

    @property
    def rancher_url(self):
        return self._rancher_url

    @property
    def rancher_api_key(self):
        return self._rancher_api_key

    @property
    def rancher_cluster_id(self):
        return self._rancher_cluster_id

    @property
    def rancher_project_id(self):
        return self._rancher_project_id

    @property
    def rancher_client(self):
        return RancherClient(self.rancher_url, self.rancher_api_key,
                             self.rancher_cluster_id,
                             self.rancher_project_id)

    def add_node(self, name, size):
        params = {
            'name': name,
            'application': 'cm_rancher_kubernetes_plugin',
            'deployment_target_id': self.connection_settings.get('deployment_target_id'),
            'application_version': '0.1.0',
            'config_app': {
                'rancher_action': 'add_node',
                'config_rancher_kube': {
                    'rancher_node_command': (
                        self.rancher_client.get_cluster_registration_command()
                        + " --worker")
                }
            }
        }
        try:
            return self.context.cloudlaunch_client.deployments.create(**params)
        except Exception as e:
            raise ValidationError(str(e))

    def remove_node(self, node):
        return self.context.cloudlaunch_client.deployments.delete(
            node.deployment.id)

    def activate_autoscaling(self, min_nodes=0, max_nodes=None, size=None):
        pass

    def deactivate_autoscaling(self):
        pass