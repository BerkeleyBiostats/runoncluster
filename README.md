runoncluster
===

Submits jobs to the tl-app

Installation
---

	pip install runoncluster

Usage
---

	runoncluster script.Rmd inputs.json config.json

Configuration
---

**RMarkdown Script***

Use the `params` feature for passing inputs to the script:

	---
	title: "Sample Script"
	output: 
	  html_document:
	    self_contained: false
	params:
	  sample_size: 10000
	---

	### Session Information

	```{r sessionInfo, echo=FALSE, results="asis"}
	sessionInfo()
	```

**inputs.json**

Set the values of parameters as key/value pairs in a json file:

	{
		"sample_size": 10000,
		"data": {
			"uri": "https://git.ghap.io/stash/scm/hbgd/ki1000111.git",
			"repository_path": "WASH-BK/adam/full_ki1000111_WASH_BK.csv"
		}		
	}

If a `data` section is included with a `git.ghap.io` URL, tl-app will clone that repo to the GHAP filesystem and replace the URI with one that points to the file specific in `repository_path`. This way your RMarkdown script can simply:

	dataset = data.table::fread(params$data$uri)

**config.json**

The configuration file lets the CLI know where to send the job. Here is an example:

	{
		"base_url": "https://tl-app-rvit.herokuapp.com/",
		"ghap_username": "${GHAP_USERNAME}",
		"ghap_password": "${GHAP_PASSWORD}",
		"ghap_ip": "${GHAP_IP}",
		"token": "${TLAPP_TOKEN}",
		"r_packages": [
			"knitr",
			"github://jeremyrcoyle/delayed@reduce-r-version",
			"igraph@1.0.1"
		]
	}

The special `${VAR_NAME}` syntax will read the value from an environment variable before pushing it to the server.

The `r_packages` section allows you to define R packages to be installed on the target system. There are a few special syntaxes supported:

* `<package_name>` installs from CRAN
* `<package_name>@<version> installs a specific version of a package from CRAN
* `github://<username>/<package_name>` installs from Github using `devtools`

Right now, you have to ask a developer for an API token. Improved UX coming soon!





