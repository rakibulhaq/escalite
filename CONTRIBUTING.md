# Contributing to This Project

Thank you for your interest in contributing! We welcome enhancements, bug fixes, or new features. Please follow these steps to make your contribution as smooth as possible.

## 1. Create an Issue

Before starting work, please [open an issue](https://github.com/rakibulhaq/escalite/issues) describing your proposed enhancement or bug fix. This helps us discuss your idea and avoid duplicate work.

- Go to the **Issues** tab.
- Click **New Issue**.
- Choose the appropriate template (feature, bug, etc.).
- Fill in the details and submit.

## 2. Fork the Repository

- Click the **Fork** button at the top right of the repository page.
- Clone your fork to your local machine:

  ```sh
  git clone https://github.com/your-username/escalite.git
  cd escalite
  ```

## 3. Create a Branch

- Create a new branch for your work:

  ```sh
  git checkout -b my-enhancement
  ```

## 4. Make Your Changes

- Implement your enhancement or bug fix.
- **Write or update tests** to cover your changes. We encourage you to aim for as much test coverage as possible!

## 5. Run Tests

- Make sure all tests pass before submitting your PR:

  ```sh
  poetry run pytest --cov
  ```

- Check the coverage report and add tests if needed.

## 6. Commit and Push

- Commit your changes with a clear message:

  ```sh
  git add .
  git commit -m "Describe your enhancement"
  git push origin my-enhancement
  ```

## 7. Create a Pull Request

- Go to your fork on GitHub.
- Click **Compare & pull request**.
- Fill in the PR template, referencing the related issue if applicable.
- Submit your pull request.

## 8. Respond to Feedback

- Be ready to discuss and update your PR based on feedback from maintainers.

---

Thank you for helping improve this project! Your contributions and thorough test coverage make the project better for everyone.