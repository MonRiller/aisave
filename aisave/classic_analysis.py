def sys_score(sys_info):
    component_vulns = {}
    for component in sys_info["components"].keys():
        component_vulns[component] = []
    for vuln in sys_info["vulnerabilities"].keys():
        for component in sys_info["vulnerabilities"][vuln]["components"]:
            component_vulns[component].append(sys_info["vulnerabilities"][vuln]["score"])

    component_raw_scores = {}
    for component in sys_info["components"].keys():
        component_raw_scores[component] = sum([score / (i + 1) for i, score in enumerate(sorted(component_vulns[component], reverse=True))])

    component_dependencies = {}
    for component in sys_info["components"].keys():
        fill_dependencies(component_dependencies, sys_info["components"], component)

    functionality_dependencies = {}
    for functionality in sys_info["functionalities"].keys():
        functionality_dependencies[functionality] = set()
        for dependency in sys_info["functionalities"][functionality]["components"]:
            functionality_dependencies[functionality] |= component_dependencies[dependency]

    functionality_scores = {}
    for functionality in sys_info["functionalities"].keys():
        functionality_scores[functionality] = sum([score / (i + 1) for i, score in enumerate(sorted([component_raw_scores[dependency] for dependency in functionality_dependencies[functionality]], reverse=True))])

    try:
        func_coef = 1 / (sum([sys_info["functionalities"][functionality]["score"] for functionality in sys_info["functionalities"].keys()]))
    except:
        func_coef = 1
    functionality_adjusted = {}
    for functionality in sys_info["functionalities"].keys():
        functionality_adjusted[functionality] = functionality_scores[functionality] * sys_info["functionalities"][functionality]["score"] * func_coef

    total_score = 0.95 ** (sum(functionality_adjusted.values()))
    return total_score, component_raw_scores, functionality_scores

def fill_dependencies(dependency_dict, component_dict, component):
    if component in dependency_dict:
        return dependency_dict[component]

    dependency_dict[component] = {component}
    for dependency in component_dict[component]["dependencies"]:
        dependency_dict[component] |= fill_dependencies(dependency_dict, component_dict, dependency)
    return dependency_dict[component]
