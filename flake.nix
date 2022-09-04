{
  description = "ADA Rewards Parser";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.05";
    cardano-node.url = "github:input-output-hk/cardano-node?tag=1.34.3";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, cardano-node }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in rec {
        packages = {
          bech32 = cardano-node.packages.${system}.bech32;

          stake-addr = pkgs.writeShellApplication {
            name = "stake-addr";
            runtimeInputs = [packages.bech32];
            text = builtins.readFile ./pkgs/stake-addr/stake-addr.sh;
          };

          stake-parsing = pkgs.callPackage ./pkgs/stake-parsing {};

          treasury-parsing = pkgs.callPackage ./pkgs/treasury-parsing {};
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            mypy
            packages.bech32
            packages.stake-addr
            packages.stake-parsing
            packages.treasury-parsing
            python3
            python3Packages.black
            python3Packages.docopt
            python3Packages.flake8
            python3Packages.ipython
          ];
        };

        devShell = devShells.default;
      }
    );
}
