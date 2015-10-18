#!/usr/bin/env bash

sphinx-build -b html docs/ docs/_build/html/
cp -R docs/_build/html/* ../rmtc-parsing-docs/
pushd ../rmtc-parsing-docs/
git add -A
git commit -m "autoupdate"
git push origin gh-pages
popd