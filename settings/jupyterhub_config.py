
import os
import docker
import socket
from dockerspawner import DockerSpawner
from firstuseauthenticator import FirstUseAuthenticator
import random
from traitlets import default
from jupyterhub.handlers import BaseHandler
import docker
import glob
from tornado.web import HTTPError
import logging

class ImageCommitHandler(BaseHandler):
    async def get(self):
        user = self.current_user
        if not user:
            raise HTTPError(403, "Only authenticated users can commit their Docker images")

        # DockerSpawner instance for the current user
        spawner = user.spawner
        if not isinstance(spawner, DockerSpawner):
            raise HTTPError(400, "This API endpoint is only available for DockerSpawner")

        # Get the prefix parameter from the request body
        repository_name = self.get_argument('repository_name', default='my-jupyter/single-user')
        if repository_name =="":
            repository_name="my-jupyter/single-user"
        # Commit the container with the image name prefixed by the prefix parameter
        commit_result = await self.commit_container(spawner, user, repository_name)

        # Return the commit result
        self.set_status(200)
        self.finish(commit_result)

    async def commit_container(self, spawner, user, repository_name=''):
        client = docker.APIClient(base_url='unix://var/run/docker.sock')

        container_id = spawner.container_id
        repo = repository_name
        tag = user.name

        try:
            commit_response = client.commit(container_id, repository=repo, tag=tag)
            commit_id = commit_response['Id']
        except docker.errors.APIError as e:
            self.log.error(f"Failed to commit container: {e}")
            raise HTTPError(500, f"Failed to commit container: {e}")

        return {"message": "Container committed successfully. \n new image=" + repo + ":" + tag}
class KillContainerHandler(BaseHandler):
    async def get(self):
        user = self.current_user
        logging.info(str(user))
        if not user:
            raise HTTPError(403, "Only authenticated users can commit their Docker images")

        # DockerSpawner instance for the current user
        spawner = user.spawner
        if not isinstance(spawner, DockerSpawner):
            raise HTTPError(400, "This API endpoint is only available for DockerSpawner")

        # Commit the container with the image name prefixed by the prefix parameter
        commit_result = await self.kill_container(spawner, user)

        # Return the commit result
        self.set_status(200)
        self.finish(commit_result)
    async def kill_container(self,spawner,user):
        client = docker.APIClient(base_url='unix://var/run/docker.sock')

        container_id = spawner.container_id

        try:
            kill_response = client.remove_container(container_id)
        except docker.errors.APIError as e:
            self.log.error(f"Failed to commit container: {e}")
            raise HTTPError(500, f"Failed to commit container: {e}")

        return {"message": "Container killed successfully. \n"}

class FindMyContainerNameHandler(BaseHandler):
    async def get(self):
        user = self.current_user
        logging.info(str(user))
        if not user:
            raise HTTPError(403, "Only authenticated users can commit their Docker images")

        # DockerSpawner instance for the current user
        spawner = user.spawner
        if not isinstance(spawner, DockerSpawner):
            raise HTTPError(400, "This API endpoint is only available for DockerSpawner")

        # Commit the container with the image name prefixed by the prefix parameter
        client =docker.DockerClient(base_url='unix://var/run/docker.sock')
        container = client.containers.get("/jupyter-"+user.name)

        image_name=str(container.image).split("'")[1].split(':')[0]
        if image_name =="":
            images = client.images.list()
            current_username = user.name
            allowed_images = [f"{img.tags[0]}" for img in images if img.tags and current_username in img.tags[0]]
            image_name=allowed_images[0].split(':')[0]


        commit_result = {"image_name":image_name}

        # Return the commit result
        self.set_status(200)
        self.finish(commit_result)




JUPYTER_HUB_CONTAINER_NAME="jupyterhub"
def get_jupyterhub_ip(container_name):
    client = docker.from_env()
    container = client.containers.get(container_name)
    container_ip = container.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']
    return container_ip

c.JupyterHub.authenticator_class = FirstUseAuthenticator
c.FirstUseAuthenticator.create_users = False
c.FirstUseAuthenticator.admin_users = {"serveradmin"}

def get_container_Names():
    client = docker.APIClient(base_url='unix://var/run/docker.sock')
    response = client.containers(all=True)
    Names=[res["Names"][0] for res in response if "jupyter-" in res["Names"][0]]
    return Names
def container_remove(container_id):
    client = docker.APIClient(base_url='unix://var/run/docker.sock')


    try:
        kill_response = client.kill(container_id)
        remove_response = client.remove_container(container_id)
        time.sleep(3)
        return True
    except docker.errors.APIError as e:
        self.log.error(f"Failed to commit container: {e}")
        raise HTTPError(500, f"Failed to commit container: {e}")

# Customize the form
def form_func(self,spawner):
    client =docker.DockerClient(base_url='unix://var/run/docker.sock')
    containers = client.containers.list()
    Recent_used_memory=0
    for container in containers:
        stats = client.api.stats(container.id,stream=False)
        print(stats)
        Recent_used_memory+=stats["memory_stats"]["limit"]// (1024**3)
       
    images = client.images.list()
    current_username = spawner.user.name

    output=""
    output2='checked="checked"'

    exist_container="/jupyter-"+current_username in get_container_Names()
    if exist_container ==True:
        output="""
        <p><font color="red">コンテナがまだ残っています。このままスタートすると停止時の自動削除以外、前回の設定と同じコンテナの続きで開始されます。</font><br>
        もし下記の設定で更新したimageでコンテナを再度作りたい場合はチェックマークを入れてください。<input type="checkbox" id="container_re_create" name="container_re_create" value="container_re_create" /></p><br>
        """
        output2=''


    # Filter images
    allowed_images = [f"{img.tags[0]}" for img in images if img.tags and current_username in img.tags[0]]
    allowed_images += [
        "jupyter/base-notebook-gpu:latest",
        "jupyter/base-notebook:latest",
    ]
    spawner.allowed_images=allowed_images
    image_options = "".join([f'<option value="{img}">{img}</option>' for img in allowed_images])

    memory_options = "".join([f'<option value="{2**i}">{2**i}GB</option>' for i in range(8) if 150-Recent_used_memory-2**i>=0 ])

    return output+f"""
    <label for="gpu">Use GPU:</label>
    <select name="gpu">
      <option value="yes">Yes</option>
      <option value="no" selected>No</option>
    </select>
    <br><br>
    <label for="workspace">Add Folder PATH:</label>
    <input name="workspace" placeholder="/path/to/folder">
    <br><br>
    <label for="image">Select Docker Image:</label>
    <select name="image">
      {image_options}
    </select>
     <br><br>
 <label>Memory Used:{Recent_used_memory} GB</label>
    <br><br>
    <label for="memory">Memory:</label>
<select name="memory" id="memory">
  {memory_options}
</select>
<br>
<p>Experiment Setting:指定のportについてホストのportとbindingを追加する。<br>
8000,8080,8888のポートはjupyterHub関係で埋まっているので無視します。<br>
<input name="port" placeholder="XXXX" type=”number”>
</p>
<br>
<p>stopしたら自動で削除する。<input type="checkbox" id="image_stop_kill" name="image_stop_kill" value="image_stop_kill" {output2}/></p>


    <br><br>
    """

c.JupyterHub.template_paths = ['templates']
#.JupyterHub.extra_handlers = [    (r"/image_save", MyAPIHandler, {"hub_auth": c.JupyterHub}),]
c.JupyterHub.extra_handlers = [
    (r"/api/image_commit", ImageCommitHandler),
    (r"/api/container_kill", KillContainerHandler),
    (r"/api/find_container_name",FindMyContainerNameHandler)
]
mem_limit="1G"
class MyDockerSpawner(DockerSpawner):
    options_form = form_func


    def options_from_form(self, formdata):
        options = {}
        options['container_re_create'] = formdata.get('container_re_create',None)
        options['gpu'] = formdata['gpu'][0]
        options['workspace'] = formdata['workspace'][0].strip()
        options['image'] = formdata['image'][0]
        options['memory'] = formdata['memory'][0]
        options['port'] = formdata['port'][0]
        options['image_stop_kill'] = formdata.get('image_stop_kill',None)
        logging.info(f"{options}")
        return options

    async def start(self):
        if self.user.name == "serveradmin":
            raise Exception("Admin user is not allowed to spawn notebooks.")
        exist_container="/jupyter-"+self.user.name in get_container_Names()

        if exist_container and self.user_options["container_re_create"] !=None:
            client =docker.DockerClient(base_url='unix://var/run/docker.sock')
            container = client.containers.get("/jupyter-"+self.user.name)
            if container.status=="running":
                container.kill()
            container.remove()
            self.log.info("container kill!")


        user_workspace_path = f"/share/workspace/{self.user.name}"
        host_workspace_path = f"C:/Users/admin/Desktop/workspace/{self.user.name}"
        
        if not os.path.exists(user_workspace_path):
            os.makedirs(user_workspace_path)
            os.chmod(user_workspace_path, 0o777)

        global mem_limit
        self.extra_host_config = {'network_mode': 'bridge'}
        self.image = self.user_options.get('image', '')
        self.log.info(f":::::::::::::::::::::::::::::::{self.image}::::::::::::::::::::::::::")
        mem_limit = str(self.user_options.get('memory', 1)) + "G"  # Convert memory value to string with 'M' suffix for MB
        self.extra_host_config.update({"mem_limit": mem_limit})
        if self.environment==None:
            self.environment={"MEM_LIMIT": mem_limit[:-1]}
        else:
            self.environment.update({"MEM_LIMIT": mem_limit[:-1]})
        workspace = self.user_options.get('workspace', '')
        self.volumes = {host_workspace_path: {"bind": "/home/jovyan/mnt_workspace", "mode": "rw"}}

        if workspace:
            self.volumes.update({workspace: {"bind": "/home/jovyan/mnt", "mode": "rw"}})
        port = self.user_options.get('port', '')
        if port:
            if int(port)!=8000 and int(port)!=8080  and int(port)!=8888 :
                print(port,type(port))
                self.extra_create_kwargs["ports"]={
                "%i/tcp" % int(port):None,"8888/tcp":None}
                self.extra_host_config["port_bindings"]= {int(port):("0.0.0.0",int(port))}
        if self.user_options.get('gpu', 'no') == 'yes':
            self.extra_host_config.update({"device_requests": [
                docker.types.DeviceRequest(
                    count=-1,
                    capabilities=[["gpu"]],
                ),
            ],})
        self.extra_create_kwargs.update({"command":"jupyter labhub"})
        if self.user_options.get("image_stop_kill",None)!=None:
            self.remove=True

        ip, port = await super().start()
        dood_ip = get_jupyterhub_ip('jupyter-'+self.user.name)
        dood_port = 8888

        return dood_ip,dood_port


        #return ip,port
c.JupyterHub.log_level=logging.DEBUG
c.JupyterHub.spawner_class = MyDockerSpawner
c.MyDockerSpawner.read_only_volumes = {"/var/run/docker.sock": "/var/run/docker.sock"}



c.MyDockerSpawner.use_internal_ip = True
c.DockerSpawner.debug = True
c.MyDockerSpawner.network_name = "bridge"


c.MyDockerSpawner.start_timeout =120

c.JupyterHub.hub_ip = get_jupyterhub_ip(JUPYTER_HUB_CONTAINER_NAME)
c.JupyterHub.hub_port = 8080 #好きなポート





