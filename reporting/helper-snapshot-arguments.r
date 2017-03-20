# Helper for various post processing scripts that are used to generate plots
# snapshots of experiments: Populates path_to_snapshot and path_to_output

args = commandArgs(trailingOnly=TRUE)

print(args)

if (length(args)==0) {
  stop("Please specify the path to a simulation snapshot.\nUsage: ./script.r PATH-TO-SNAPSHOT [optional: PATH-TO-OUTPUT]", call.=FALSE)
} else if (length(args)==1) {
  # default output path
  args[2] = "./"
}

path_to_snapshot = "./2017-03-16T17:15:39.685334_43f835ce2f"
path_to_output = path_to_snapshot
dir.create(file.path(path_to_output, "plots"), showWarnings = TRUE)
path_to_output = paste(path_to_snapshot, "/plots/", sep="")

print("snapshot argument helper completed")
