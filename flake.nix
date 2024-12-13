{
  description = "Dev environment with Python 3.12 and Node.js 23 for a FastAPI + Vue3 project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
      };
    in {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pkgs.python312Full
          pkgs.python312Packages.fastapi
          pkgs.python312Packages.uvicorn
          pkgs.python312Packages.numpy
          pkgs.nodejs_23
          pkgs.yarn
        ];
      };
    };
}
