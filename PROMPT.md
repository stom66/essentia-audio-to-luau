Prompt used for chatgpt:


Let write some code. Be succinct with your repsonses, straight to the point, without the extra waffle and zoomerisms where you congratulate me on my patience, applaud my efforts at copy and pasting code, and praise me like you're a human. Please just be an efficient, accurate, and reliable source of code generation.

I need a Python script with a clearly defined, callable function:

	def extract_features_to_luau(audio_path, output_path):

This function should be importable and directly usable from other scripts. It must:

    - Load and process the audio file specified by audio_path.
	- perform a low-pass filter to ignore anything over 5khz - washy bullshit, cymbols etc
	- Extract rhythmic features: 
		- an array of timestamps for beats detected
		- pitch-based note names at each beat
		- tempo (BPM)

	- Should use the following data structure for the return:
		return {
			beats = {}, -- table of beat timestamps
			notes = {}, -- table of beat notes
			tempo = 0, -- number of tempo
			duration = 24 -- song length in seconds
		}

    - Return these features in a dictionary and write them as a Lua table to output_path using to_lua_table from the luau_writer module, eg:
	
		from luau_writer import to_lua_table
		with open(output_path, 'w') as f:
			f.write('return ')
			f.write(to_lua_table(features_dict))
			f.write('\n')

    - call an existing function to plot a graph of the results:
	
		from plot_features import plot_features
    	plot_features(audio_path, result, output_path.replace('.luau', '_debug.png'))

	- check that all beats actually exist, eg have a function filter_silence which can be run on the results

	- Extend the audio slightly with padding to give beat detection a chance to resolve boundary beats.

The code should:

    - Use reliable libraries like librosa, madmom, essentia, or others suitable for the task.
    - Be robust against invalid or silent audio.
    - Include all necessary imports and be self-contained within a file (e.g., feature_extractor.py).
    - Avoid any undefined functions or assumptions.

This should make it easy to call the feature extraction from other Python scripts by importing the module and calling extract_features_to_luau().