# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.nodejs_20
    pkgs.mongodb
    pkgs.mongosh
  ];

  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "ms-python.python"
      "rangav.vscode-thunder-client"
    ];

    previews = {
      enable = true;
      previews = {
        backend = {
          command = ["/bin/sh" "-c" "cd backend && pip install -r requirements.txt && uvicorn main:app --reload --host 0.0.0.0 --port $PORT"];
          manager = "web";
          env = {
            PORT = "$PORT";
          };
        };
        frontend = {
          command = ["npm" "run" "dev" "--prefix" "frontend" "--" "--port" "$PORT" "--host" "0.0.0.0"];
          manager = "web";
          env = {
            PORT = "$PORT";
          };
        };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        # Example: install JS dependencies from NPM
        # npm-install = "npm install";
      };
      # Runs when the workspace is (re)started
      onStart = {
        # Example: start a background task to watch and re-build backend code
        # watch-backend = "npm run watch-backend";
        start-mongo = "mongod --fork --logpath /tmp/mongod.log --dbpath .idx/mongo_data --bind_ip 127.0.0.1";
      };
    };
  };
}
