import argparse
import allensdk.core.json_utilities as ju
import numpy as np
import biophys_optimize.neuron_passive_fit as npf

import argschema as ags

class PassiveFittingPaths(ags.schemas.DefaultSchema):
    swc = ags.fields.InputFile(description="path to SWC file")
    up = ags.fields.InputFile(descritpion="up data path")
    down = ags.fields.InputFile(descritpion="down data path")
    passive_info = ags.fields.InputFile(description="passive info file")
    fit = ags.fields.List(ags.InputFile,
        description="list of passive fitting files",
        cli_as_single_argument=True)
    passive_fit_results_file = ags.fields.OutputFile(description="passive fit results file")


class PassiveFittingParameters(ags.ArgSchema):
    paths = ags.fields.Nested(PassiveFittingPaths)
    passive_fit_type = ags.fields.Str(description="passive fit type")


def main(paths, passive_fit_type, output_json, **kwargs):
    info = ju.read(paths["passive_info"])
    if not info["should_run"]:
        ju.write(output_json, { "paths": {} })
        return

    swc_path = paths["swc"].encode('ascii', 'ignore')
    up_data = np.loadtxt(paths["up"])
    down_data = np.loadtxt(paths["down"])
    results_file = paths["passive_fit_results_file"]

    npf.initialize_neuron(swc_path, paths["fit"])

    if passive_fit_type == npf.PASSIVE_FIT_1:
        results = npf.passive_fit_1(up_data, down_data,
            info["fit_window_start"], info["fit_window_end"])
    elif passive_fit_type == npf.PASSIVE_FIT_2:
        results = npf.passive_fit_2(up_data, down_data,
            info["fit_window_start"], info["fit_window_end"])
    elif passive_fit_type == npf.PASSIVE_FIT_ELEC:
        results = npf.passive_fit_elec(up_data, down_data,
            info["fit_window_start"], info["fit_window_end"],
            info["bridge"], info["electrode_cap"])
    else:
        raise Exception("unknown passive fit type: %s" % passive_fit_type)

    ju.write(results_file, results)
    ju.write(output_json, { "paths": { passive_fit_type: results_file } })


if __name__ == "__main__":
    module = ags.ArgSchemaParser(schema_type=PassiveFittingParameters)
    main(**module.args)
