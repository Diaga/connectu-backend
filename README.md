![connectu-backend](https://socialify.git.ci/Diaga/connectu-backend/image?description=1&language=1&pattern=Signal&theme=Light)


## Contributing

### Setup the environment

1. Download and install [latest version of git](https://git-scm.com/downloads).
1. Clone the repository locally
     ```shell script
    $ git clone https://github.com/Diaga/connectu-backend.git
    $ cd connectu-backend
    ```
1. Create a virtualenv.
    ```shell script
    $ python3 -m venv venv
    $ . venv/bin/activate
    ```
    On Windows, activating is different.
    ```shell script
    $ venv/Scripts/activate
    ```
1. Install python dependencies
    ```shell script
    $ pip install -r requirements.txt
    ```
1. Install the pre-commit hooks.
    ```shell script
    $ pre-commit install
    ```

### We Use [GitHub Flow](https://guides.github.com/introduction/flow/index.html), So All Code Changes Happen Through Pull Requests
Pull requests are the best way to propose changes to the codebase (we use GitHub Flow). We actively welcome your pull requests:

1. Create your branch from master.
1. If you've added code that should be tested, add tests.
1. If you've changed APIs, update the documentation.
1. Ensure the test suite passes.
1. Make sure your code lints.
1. Create that pull request!

### Commit Message and Pull Request Title
Commit message and pull request title should follow Conventional Commits.

An easy way to achieve that is to install [commitizen](https://github.com/commitizen/cz-cli) and run git cz when committing.
