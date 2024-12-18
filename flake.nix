{
  description = "Flake for Node.js 23 and Python 3.12 environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShell = pkgs.mkShell {
          name = "ai-realtime-game";

          packages = [
            pkgs.nodejs_23

            pkgs.python312
            pkgs.python312Packages.pip
            pkgs.python312Packages.uvicorn

            pkgs.yarn
            pkgs.git
          ];

          shellHook = ''
            echo "Environment ready. Happy coding!"
          '';
        };
      });
}
