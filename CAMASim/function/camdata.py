import numpy as np
from collections import defaultdict
import math

class CAM:
	def __init__(self, mats_per_bank = 1, arrays_per_mat  = 1, subarray_per_array = 1, subarray_cols = 64, subarray_rows = 64, initial_value_in_cells=0):
		self.initial_value_in_cells 		= initial_value_in_cells
		self.data 				= np.zeros(shape=(mats_per_bank,arrays_per_mat, subarray_per_array, subarray_rows, subarray_cols)) + initial_value_in_cells
		self.mats_per_bank 		= mats_per_bank
		self.arrays_per_mat 	= arrays_per_mat 
		self.subarray_per_array = subarray_per_array
		self.subarray_cols 		= subarray_cols
		self.subarray_rows 		= subarray_rows
		self.subarray_shape		= (subarray_rows, subarray_cols)

		self.subarray_in_array_cols = subarray_per_array
		self.subarray_in_array_rows = 0
		self.subarray_not_used = 0

		self.word_size = 0

		self.subarray_energy = 75

		pass

	def write(self, data_to_write: np.array):
		assert len(data_to_write.shape) == 2 or data_to_write.shape == self.data.shape, "The data has to be exactly the size of the specified architcture, or a 2D np.array" 

		assert data_to_write.size <= self.data.size, f"We cannot fit the data in the architecture total size of architecture: {self.data.size} vs total size your data {data_to_write.size}"

		if data_to_write.shape == self.data.shape:
			self.data = data_to_write.shape
			return 
		
		rows_to_write, cols_to_write = data_to_write.shape

		self.word_size = cols_to_write
		self.subarray_in_array_cols = round(cols_to_write/self.subarray_cols + 0.499) 
		self.subarray_in_array_rows = self.subarray_per_array//self.subarray_in_array_cols 
		self.subarray_not_used = self.subarray_per_array%self.subarray_in_array_cols


		assert rows_to_write <= self.mats_per_bank * self.arrays_per_mat * self.subarray_in_array_rows * self.subarray_rows, "Not able to fit"
		data_row_idx = 0

		mat_in_bank_idx = 0
		array_in_mat_idx = 0
		subarray_in_array_idx = 0
		while data_row_idx < rows_to_write:
			data_row_idx_max =  min(data_row_idx + self.subarray_rows, rows_to_write)
			for i in range(self.subarray_in_array_cols):				
				current_array = data_to_write[data_row_idx:data_row_idx_max,(i*self.subarray_cols):((i+1)*self.subarray_cols)]
				current_shape = current_array.shape

				pad_width = [(0, max(0, self.subarray_shape[i] - current_shape[i])) for i in range(len(self.subarray_shape))]
				
				padded_array = np.pad(current_array, pad_width=pad_width, mode='constant', constant_values=self.initial_value_in_cells)
				self.data[mat_in_bank_idx,array_in_mat_idx,subarray_in_array_idx,:,:] = padded_array
				subarray_in_array_idx += 1 
			data_row_idx = data_row_idx_max
				
			if subarray_in_array_idx > self.subarray_in_array_rows:
				subarray_in_array_idx = 0

				if (array_in_mat_idx := array_in_mat_idx + 1) > self.arrays_per_mat:
					array_in_mat_idx = 0

					if (mat_in_bank_idx := mat_in_bank_idx + 1) > self.mats_per_bank:
						raise Exception("Cannot fit in memory")
		

	def search(self, query: np.array, allow_ngram: bool =False, indices_to_search: np.array =np.array([]), calculate_energy=False):
		# assert (len(query.shape) == 1 and (len(query) == self.data.shape[-1] and self.subarray_in_array_cols == 1) or allow_ngram, (
		# 	f"Query length ({len(query)}) does not match the last dimension of data ({self.data.shape[-1]}). "
		# 	"Set allow_ngram=True for partial word search."
		# )
		# If subarray_in_array_cols is == 1, No horizontal merge is required
		if self.subarray_in_array_cols == 1:
			if len(indices_to_search) > 0:
				results_idx = np.where((self.data[tuple(indices_to_search.T)][...,:len(query)] == query).all(axis=-1))
				results_stack = indices_to_search[results_idx]
				
			else:
				results = np.where((self.data[...,:len(query)] == query).all(axis=-1)) # gget results
				results_stack = np.stack(results).T # each row is a index in bank-mat-array, subarray 
			
			if calculate_energy:
				percentage_activated_rows = len(indices_to_search)/(self.data.size/self.subarray_cols) if len(indices_to_search) > 0 else 1
				percentage_activated_cols = len(query)/self.subarray_cols
				print(self.subarray_energy * 0.5 * (percentage_activated_cols  +  percentage_activated_rows ))
		else:
			all_idx = []
			grouped = defaultdict(list)
			results = []			
			for i in range(self.subarray_in_array_cols): 
				q = query[i*self.subarray_cols:min(i*self.subarray_cols + self.subarray_cols, self.word_size)]
				r = np.where((self.data[...,list(range(i,self.subarray_in_array_rows* self.subarray_in_array_cols, self.subarray_in_array_cols)),:,:len(q)] == q).all(axis=-1))
				idx = np.stack(r)
				idx[-2] = self.subarray_in_array_cols*idx[-2] + i
				all_idx.append(idx.T)
			all_idx = np.vstack(all_idx)

			for row in all_idx:
				# the will be per bank, mat, which row in the array is, and per rown in subarray
				key = (row[0], row[1], math.floor(row[2]/self.subarray_in_array_cols),row[3])
				grouped[key].append(row)


			for key, group in grouped.items():
				# this is where we can add magic to the horizontal merging
				if len(group) == self.subarray_in_array_cols:
					results.append(group[0])
			results_stack = np.vstack(results)		


		return results_stack