{
  python3Packages,
}:
with python3Packages;

buildPythonPackage rec {
  pname = "bf-stake-parsing";
  version = "1.0.0";

  propagatedBuildInputs = [
    docopt
    requests
  ];

  src = ./.;
}
