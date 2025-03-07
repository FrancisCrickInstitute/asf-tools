# Refactoring Code: Splitting Samples by Project Type

## 1) Lines 131-134 + 146-160
We can refactor this section to make it more modular by introducing a function:

### **Possible function name:**
```python
def split_by_project_type(self, samples_all_info, constants_dict):
```

### Constants Dictionary Structure
```python
constants_dict = {
    "CONSTANT_NAME": [list of values],
    "SINGLE_CELL_PROJECT_TYPES": [list of values],
    "ATAC_PROJECT_TYPES": [list of values],
    "DLP": [list of values],
}
```
- "other_samples" (bulk) can be filtered inside the function, rather than being required as an external input.

### Expected Output Structure
```
output_dict = {
    "dlp_samples": [sample_info],
    "single_cell_samples": {sample: info, sample: info, ...},
    "atac_samples": {sample: info},
    "other_samples": {sample: info}
}
```

### **How it would work**
1. For each category in `constants_dict`, an entry is added in `output_dict`.
2. The key is the constant name, and the value is a list of sample names whose `Project_type` or `Data_analysis_type` matches any of the values in that category.
3. Samples that don't match any category are assigned to `"other_samples"`.

### **Important Considerations**
- The current code filters `samples_all_info` to only keep:
  - `sample_name`
  - `lane`
  - `index`
  - `index2`
- Then, only this filtered information is added to the lists.
- We have a few options for handling filtering:
  1. Only add `sample_name` to `output_dict`, and append the appropriate info outside this function.
  2. Import the already filtered dictionary (samples_bcldata_dict).
  3. Perform filtering inside this function.

---

### Draft refactored code
```python
def split_by_project_type(samples_all_info, samples_bcldata_dict, project_types_dict):
    """
    Dynamically categorizes samples based on project type and data analysis type.

    Args:
        samples_all_info (dict): Dictionary containing metadata for all samples.
        samples_bcldata_dict (dict): Dictionary containing BCL data for samples.
        project_types_dict (dict): Dictionary mapping category names to lists of valid values.

    Returns:
        dict: A dictionary containing categorized samples for each project type.
    """
    # Initialize result dictionary dynamically with empty dictionaries
    categorized_samples = {category.lower(): {} for category in project_types_dict}

    # Add other_samples explicitly since they're handled differently
    categorized_samples["other_samples"] = {}

    for sample, info in samples_all_info.items():
        project_type = info.get("project_type")
        data_analysis_type = info.get("data_analysis_type")

        if project_type is None:
            log.warning(f"'{sample}' has None project_type.")
            continue

        categorized = False  # Flag to track if the sample was categorized

        # Dynamically check and assign samples to the correct category
        for category, valid_types in project_types_dict.items():
            if project_type in valid_types or data_analysis_type in valid_types:
                categorized_samples[category.lower()][sample] = samples_bcldata_dict[sample]
                categorized = True
                break  # Stop checking once categorized

        # Handle DLP samples separately
        if not categorized:
            categorized_samples["other_samples"][sample] = samples_bcldata_dict[sample]

    return categorized_samples
```

## 2) Lines 178–279: Processing Each Entry

For each entry in the `output_dict` (from the previous step), we initiate the associated processing.

### Processing Logic:
- If `output_dict.key == "dlp"` → Start **DLP processing**.
- If `output_dict.key == "single_cell"` → Start **Single Cell processing**.
- If `output_dict.key == "atac"` → Start **ATAC processing**.
- If `output_dict.key == "other_samples"` → Start **Other Samples processing**.

Each category requires its own subprocess.

### Required Subprocesses
We need to create **four subprocesses**:

**DLP Processing**
**Required Inputs:**
- `filtered_dlp_samples`
- `dlp_sample_file`
- `samplesheet_name`
- `output_path`
- `header_dict`
- `reformatted_reads_dict`
- `bcl_settings_dict`

 **Single Cell Processing**
**Required Inputs:**
- `filtered_single_cell_samples`
- `samplesheet_name`
- `output_path`
- `header_dict`
- `reformatted_reads_dict`
- `bcl_settings_dict`

**ATAC Processing**
**Required Inputs:**
- `filtered_atac_samples`
- `original_sample_info` (for all ATAC samples)
- `samplesheet_name`
- `output_path`
- `header_dict`
- `reformatted_reads_dict`
- `bcl_settings_dict`

**Other Samples Processing**
**Required Inputs:**
- `filtered_other_samples`
- `flowcell_id`
- `runinfo_path`
- `samplesheet_name`
- `output_path`
- `header_dict`
- `reformatted_reads_dict`
- `bcl_settings_dict`

### **Important Considerations**
Some of these inputs are repeated and not changed across the different categories, such as `header_dict`, `reformatted_reads_dict`, and `bcl_settings_dict`.
An alternative approach is that each subprocess returns only the values that differ for each category in a list. Then, we can perform the following for each category:

1. **Extract category-specific values**: Each subprocess processes the category-specific data and returns only what's necessary (e.g., samples or sample information) in a list. Each entry in the list is an individual input in `generate_bcl_samplesheet`.
2. **Reuse unchanged input values**: The unchanged input values (`header_dict`, `reformatted_reads_dict`, `bcl_settings_dict`) are passed only once when calling `generate_bcl_samplesheet()`, alongside the category-specific data.

For example:

```python
for info in processed_atac_sample_list:
    for category, category_data in category_list:
        generate_bcl_samplesheet(category_data, unchanged_input_values)
```
However, I'm unsure how this approach applies for `other_samples`, as its data may require special handling. Further adjustments may be needed to accommodate its specific needs while still reusing the unchanged inputs effectively.
