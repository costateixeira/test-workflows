# ImplementationGuide Publisher GitHub Action

This GitHub Action automatically builds and publishes FHIR Implementation Guides using the HL7 FHIR IG Publisher. It is designed to run the publisher on push or pull request events and publish the output to GitHub Pages.

## Features

- Default branch is published in `https://<owner>.github.io/<repo>`. Branches are published in `https://<owner>.github.io/<repo>/branches/<branch>`
- Automatically uses the latest versions of sushi and IG publisher

## Prerequisites

Before you can use this GitHub Action, you need to ensure the following:

- Your repository should have a branch called `gh-pages`.
- You have configured GitHub Pages to serve from the `gh-pages` branch.
- Write permissions are granted for workflows
- Your FHIR IG source files are properly set up in your repository.

## Setup

1. **Configure GitHub Pages**

   Make sure that GitHub Pages is enabled for your repository and is set to deploy from the `gh-pages` branch.

2. **Add the Workflow File**

   Create a `.github/workflows` directory in your repository if it doesn't already exist, and call this workflow:
```yaml
jobs:
  call_build: 
    uses: WorldHealthOrganization/smart-base/.github/workflows/ghbuild.yml@main
```

See [example](https://github.com/WorldHealthOrganization/smart-ig-starter-kit/blob/main/.github/workflows/ghbuild.yml).

3. **GitHub Token**

   This action uses the `GITHUB_TOKEN` provided by GitHub Actions, so you don't need to manually create one.

## Usage

The action is configured to run on push or pull requests to any branch except the `gh-pages` branch. It can also be triggered manually via the GitHub Actions tab.

### Workflow Triggers

- **Push to `main` branch**: When commits are pushed to the `main` branch, the IG Publisher is run, and the output is published to the root of the GitHub Pages site.
- **Push to other branches**: When commits are pushed to branches other than `main`, the output is published to a subdirectory named after the branch - branches/<vranch_name>
- **Pull Request**: The action will run to ensure that the IG Publisher can build the IG from the pull request, but will not deploy to GitHub Pages.
- **Manual Trigger**: You can manually trigger the workflow from the GitHub Actions tab if needed.

### What the Workflow Does

Here is a step-by-step description of the workflow:

1. **Checkout**: Checks out the repository code.
2. **Get the latest image of the IG publisher**: Downloads the latest `publisher.jar` from the official FHIR IG Publisher repository.
4. **Create package cache folder**: Creates a cache folder for the packages needed by the publisher.
5. **Run the IG publisher**: Executes the IG Publisher to generate the IG site files.
6. **Deploy to GitHub Pages**: Depending on the branch, deploys the output to the `gh-pages` branch of your repository.

### Notes

- The action is currently set up to keep a history of deployments for branches other than `main`. This can be changed by adjusting the `single-commit` and `clean` options in the workflow file.


## Contributing

Contributions to this GitHub Action are welcome. Please feel free to submit issues or pull requests with improvements.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use it and contribute.
