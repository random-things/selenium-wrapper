# Changelog

## [Unreleased]

### 2023-04-09

💥 Browser action has been renamed from `wait` to `wait_for_user`  
✨ Added a `find_elements` method to `SeleniumBrowser` wrapping the driver's `find_elements` method   
✨ When using the `type` element action, a literal \n will send the return key  
✅ Test for Firefox skipped if Firefox is not installed  
📝 Fixing typos in documentation  

### 2023-04-08

✨ New browser action: `wait` that sleeps for `args.duration` seconds  
✨ Preliminary support for non-Chrome browsers

### 2023-03-22

💥 The parameter in `SeleniumElementTypeActionArgs` is now `text` instead of `string_to_type`  
✨ `action` can now include spaces in the name, e.g., `new tab` instead of `new_tab` which
makes for more readable YAML  
✨ New browser action: `new_tab`  
✨ When the `switch_tab` action is used, the browser will try to match on either title or URL
in the `tab` parameter  
✨ `SeleniumBrowser` now tries to instantiate itself as an instance of `EventFiringWebDriver`  
This support is still experimental and is only used to print events to the console. The events
cannot be hooked at this point.  
📝 Added documentation on `SeleniumBrowserActionArgs` and `SeleniumElementActionArgs`  
📝 Documentation updated to reflect changes to `SeleniumElementTypeActionArgs`  
📝 Fixing typos in documentation  
✅ Tests added for browser actions `new_tab` and `switch_tab`  
🏗️ `ExpectedConditions` is now a `CaseInsensitiveSpaceStrEnum`, so you can `wait_for` `presence_of_element_located` or `presence of element located`   

### 2023-03-08

✨ Adopting gitmoji as the commit message standard. Ref: https://gitmoji.dev/  
✨ Adding new element actions: `delete`, `insert`, `insert_trusted`, and `set_attribute`  
👷 Adding `.gitlab-ci.yml` for automated build/testing  
👷 Adding `Dockerfile` for automated build  
📝 Updating documentation to reflect the new standard  
📝 Fixing examples in `README.md`  
✅ Tests for actions that modify browser contents  
💚 Adding Docker detection to SeleniumBrowser to force headless mode  
💡 Updating some old docstrings to align with current code

### 2023-03-07

✨ `run_yaml` method that runs a series of actions based on a YAML string  
♻️ Code from `run_json` was abstracted into `run_actions` to support `run_yaml`    
✅ Test for `run_yaml` added  

### 2023-03-06

✨ `ElementActionArgs` now has an `inject` parameter that will inject the action
into the browser instead of trying to apply it externally.
This prevents "the element is not clickable" errors    
✨ `SeleniumElementActions` now has a `change` method that is used to interact
with form elements. At the moment, this only supports changing the value of
`<select>` elements  

### 2023-03-04

💥 Separated `action` into `target` (`browser | element`) and `action`  
✨ JSON-based interface using `run_json`  
✨ `wait_for_download` method  

---

## Key (in descending priority order):

🎉 = Project started  
🔖 = Release / Version tags  
🚑 = Critical hotfix  
💥 = Breaking change  
🔒 = Fix security issue  
🔐 = Add or update secrets  
✨ = Feature addition  
🔥 = Feature or code removal  
⬆️ = Dependency upgrade  
⬇️ = Dependency downgrade  
📌 = Pin dependencies to specific versions  
➕ = Dependency addition  
➖ = Dependency removal  
🐛 = Bug fix  
🌐 = Internationalization and localization  
👷 = Add or update CI build system  
💄 = Add or update UI/style files  
📈 = Add or update analytics/tracking code  
📝 = Documentation
🔧 = Add or update configuration files  
🔨 = Add or update development scripts  
⚡ = Performance improvement  
✅ = Test added or updated  
🧪 = Failing test added  
🚨 = Fix compiler/linter warnings  
🚧 = Work in progress  
💚 = CI/CD fix  
🚀 = Deployment  
✏️ = Fix typos  
💩 = Write bad code that needs improvement  
⏪ = Revert changes  
🔀 = Merge branches  
📦 = Add or update compiled files or packages  
👽 = Update code due to external API changes  
🚚 = Move or rename resources (e.g.: files, paths, routes)    
📄 = Add or update license  
🍱 = Add or update assets  
♿ = Improve accessibility  
💡 = Add or update comments in source code  
🍺 = Write code drunkenly  
💬 = Add or update text and literals  
🗃️ = Perform database related changes  
🔊 = Add or update logs  
🔇 = Remove logs  
👥 = Add or update contributor(s)  
🚸 = Improve user experience / usability  
🏗️ = Make architectural changes  
📱 = Work on responsive design  
🤡 = Mock things  
🥚 = Add or update an easter egg  
🙈 = Add or update .gitignore file  
📸 = Add or update snapshots  
⚗️ = Perform experiments  
🔍 = Improve SEO  
🏷️ = Add or update types  
🌱 = Add or update seed files  
🚩 = Add, update, or remove feature flags  
🥅 = Catch errors  
💫 = Add or update animations and transitions  
🗑️ = Deprecate code that needs to be cleaned up  
🛂 = Work on code related to authorization, roles, and permissions  
🩹 = Simple fix for a non-critical issue  
🧐 = Data exploration/inspection  
⚰️ = Remove dead code  
👔 = Add or update business logic  
🩺 = Add or update healthcheck  
🧱 = Infrastructure-related changes  
🧑‍💻 = Improve developer experience  
💸 = Add sponsorships or money-related infrastructure  
🧵 = Add or update code related to multithreading or concurrency  
🦺 = Add or update code related to validation  
