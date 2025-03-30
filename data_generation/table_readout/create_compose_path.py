import os
import sys
import pandas as pd
import numpy as np
import random
from names import products, months
import random
import matplotlib.pyplot as plt
from PIL import Image

import argparse
from tqdm import tqdm
import json


parser = argparse.ArgumentParser()
parser.add_argument("--seed", default=0, type=int)
parser.add_argument("--num_data", default=1, type=int)

parser.add_argument("--min_rows", default=5, type=int)
parser.add_argument("--min_cols", default=5, type=int)
parser.add_argument("--max_rows", default=10, type=int)
parser.add_argument("--max_cols", default=10, type=int)

parser.add_argument("--gap", default=1, type=int)
parser.add_argument("--npieces", default=1, type=int)

parser.add_argument("--output_dir", default=".", type=str)
args = parser.parse_args()


initial_seed = args.seed
seed = initial_seed

args.output_dir += "/compositional_"+str(args.gap)+"_npieces_"+str(args.npieces)
os.makedirs(args.output_dir, exist_ok=True)
random.seed(seed)
np.random.seed(seed)
print (seed)

def numpy_random_randint(max_item, num_items):
    return np.random.randint(max_item, num_items)

def numpy_random_choice(max_item, size, replace=True):
    return np.random.choice(max_item, size, replace=replace)

def numpy_random_random_sample():
    return np.random.random_sample()


def random_randint(min_, max_):
    return numpy_random_choice(range(min_, max_+1), 1)[0]


def random_sample(items, num_items):
    return numpy_random_choice(items, num_items, replace=False)

def linear_horizontal(curr_r, curr_c, top_boundary, bottom_boundary, left_boundary, right_boundary, mov_c):
    all_mvmt = []
    gap = 0 
    while (True):
        if curr_c+mov_c < left_boundary+gap or curr_c+mov_c > right_boundary-gap:
            break
        all_mvmt += [(curr_r, curr_c+mov_c)]
        curr_c+=mov_c
    return all_mvmt


def linear_vertical(curr_r, curr_c, top_boundary, bottom_boundary, left_boundary, right_boundary, mov_r):
    all_mvmt = []
    gap = 0 
    while (True):
        if curr_r+mov_r < top_boundary+gap or curr_r+mov_r > bottom_boundary-gap:
            break
        all_mvmt += [(curr_r+mov_r, curr_c)]
        curr_r+=mov_r
    return all_mvmt



#'''
def zigzag_path(df, p=0.5, npieces=2, gap=2):


    reverse_dir = numpy_random_choice(2, 1, replace=False)[0]
    option = numpy_random_choice(4, 1, replace=False)[0]

    if reverse_dir == 0:
        option_ = option 
        sign_r = 1 - 2*(option//2)
        sign_c = 1 - 2*((option//2 + option%2)%2)

        direction = option  # Start in the direction given by the option (0: right, 1: down, 2: left, 3: up)
    else:
        direction = (option+1)%4  # Start in the direction given by the option (0: right, 1: down, 2: left, 3: up)
        option_ = option 
        sign_r = 1 - 2*(option//2)
        sign_c = 1 - 2*((option//2 + option%2)%2)
    
    
    start_r = (len(df) - (option//2)) % len(df)
    start_c = (len(df.columns) - (option//2 + option%2)%2) % len(df.columns)
    

    n, m = len(df), len(df.columns)
    path_info = []  # List to store the coordinates of the path

    top, bottom = 0, n - 1
    left, right = 0, m - 1

    r, c = start_r, start_c
    
    tot_pieces = 1
    path_info.append({
            'row_idx': r,
            'col_idx': c,
            'row_name': df.index[r],
            'col_name': df.columns[c],
            'value': df.iloc[r, c],
            'piece': tot_pieces
    })
    ## print (df)

    while top <= bottom and left <= right:
        
        if tot_pieces > npieces: break
        # Move according to the current direction
        counter = 0
        if direction == 0 or direction == 2:  # Moving right (0)/left (2) (jaw opening wide)
            
            all_mvmt = linear_horizontal(r, c, top, bottom, left, right, mov_c=1-direction)
            
            for (cell_x, cell_y) in all_mvmt:
                path_info.append({
                        'row_idx': cell_x,
                        'col_idx': cell_y,
                        'row_name': df.index[cell_x],
                        'col_name': df.columns[cell_y],
                        'value': df.iloc[cell_x, cell_y],
                        'piece': tot_pieces
                })

            
            if len(all_mvmt) != 0:
                r, c = all_mvmt[-1][0], all_mvmt[-1][1]

            r += sign_r
            if r < len(df) and r > 0:
                if sign_r == 1:
                    top += 1
                elif sign_r == -1:
                    bottom -= 1
                if top > bottom: break

                path_info.append({
                        'row_idx': r,
                        'col_idx': c,
                        'row_name': df.index[r],
                        'col_name': df.columns[c],
                        'value': df.iloc[r, c],
                        'piece': tot_pieces
                })
                
            else:
                break

            r += sign_r
            if r < len(df) and r > 0:
                if sign_r == 1:
                    top += 1
                elif sign_r == -1:
                    bottom -= 1
                if top > bottom: break

                path_info.append({
                        'row_idx': r,
                        'col_idx': c,
                        'row_name': df.index[r],
                        'col_name': df.columns[c],
                        'value': df.iloc[r, c],
                        'piece': tot_pieces
                })
            else:
                break

            # now decide whether to move spiral or sinusoidal in the next step
            new_direction_decision = numpy_random_choice(2, 1, replace=False)[0] 
            if direction == 0:
                if new_direction_decision == 0:
                    # move up/down like spiral
                    direction = 2 - sign_r
                else:
                    # move left like sinusoidal
                    direction = 2
            elif direction == 2:
                if new_direction_decision == 0:
                    # move up/down like spiral
                    direction = 2 - sign_r
                else:
                    # move right like sinusoidal
                    direction = 0
            sign_c = sign_c*-1
        elif direction == 1 or direction == 3:  # Moving down (1)/up (3) (jaw opening wide)
            # decide between curvy movement or horizontal movement

            all_mvmt = linear_vertical(r, c, top, bottom, left, right, mov_r=2-direction)
            
            for cell_x, cell_y in all_mvmt:
                path_info.append({
                        'row_idx': cell_x,
                        'col_idx': cell_y,
                        'row_name': df.index[cell_x],
                        'col_name': df.columns[cell_y],
                        'value': df.iloc[cell_x, cell_y],
                        'piece': tot_pieces
                })

            if len(all_mvmt) != 0:
                r, c = all_mvmt[-1][0], all_mvmt[-1][1]

            c += sign_c
            if c < len(df.columns) and c > 0:
                if sign_c == 1:
                    left += 1
                elif sign_c == -1:
                    right -= 1
                if left > right: break

                path_info.append({
                        'row_idx': r,
                        'col_idx': c,
                        'row_name': df.index[r],
                        'col_name': df.columns[c],
                        'value': df.iloc[r, c],
                        'piece': tot_pieces
                })
                
            else:
                break

            c += sign_c
            if c < len(df.columns) and c > 0:
                if sign_c == 1:
                    left += 1
                elif sign_c == -1:
                    right -= 1
                if left > right: break
                
                path_info.append({
                        'row_idx': r,
                        'col_idx': c,
                        'row_name': df.index[r],
                        'col_name': df.columns[c],
                        'value': df.iloc[r, c],
                        'piece': tot_pieces
                })
                
            else:
                break

            # now decide whether to move spiral or sinusoidal in the next step
            new_direction_decision = numpy_random_choice(2, 1, replace=False)[0] 
            if direction == 1:
                if new_direction_decision == 0:
                    # move up/down like spiral
                    direction = 1 - sign_c
                else:
                    # move left like sinusoidal
                    direction = 3
            elif direction == 3:
                if new_direction_decision == 0:
                    # move up/down like spiral
                    direction = 1 - sign_c
                else:
                    # move up/down like sinusoidal
                    direction = 1
            sign_r = sign_r*-1
        tot_pieces += 1
    skipped_cells = numpy_random_choice([0, 1,], 2, replace=True)

    if skipped_cells[1] != 0:
        path_info = path_info[skipped_cells[0]: -skipped_cells[1]]
    else:    
        path_info = path_info[skipped_cells[0]:]
    
    reverse_move = numpy_random_choice(2, 1, replace=False)[0]
    if reverse_move == 1:
        path_info = path_info[::-1]
    return path_info


def color_path(df, path):
    bg = pd.DataFrame('', index=df.index, columns=df.columns)
    ## print (path)
    for entry in path:
        bg.loc[entry['row_name'], entry['col_name']] = 'background-color:yellow'
    return bg


# Generate 2D tables with meaningful rows and columns

def generate_business_sales_data(num_rows, num_cols, p=0.5):
    product_names = products
    rows = random_sample(product_names, num_rows)
    columns = random_sample(months, num_cols)
    data = numpy_random_choice(10, size=(num_rows, num_cols)) 
    table = pd.DataFrame(data, index=rows, columns=columns)
    path = zigzag_path(table, p, npieces=args.npieces, gap=args.gap)
    return table.style.apply(lambda t: color_path(t, path), axis=None), path

# Generate multiple tables for each category with varying number of rows and columns
def generate_tables(generator_function, num_tables, min_rows=5, min_cols=5, max_rows=10, max_cols=10, p=0.5):
    tables = []
    paths = []
    for _ in tqdm(range(num_tables)):
        num_rows = random_randint(min_rows, max_rows)
        num_cols = random_randint(min_cols, max_cols)
        table, path = generator_function(num_rows, num_cols, p)
        tables.append(table)
        paths.append(path)
    return tables, paths

# Function to apply asterisks to specific cells
def mark_cells_with_asterisk(styler, path_info):
    def apply_mark(df):
        # Modify cell values based on path_info
        # We use df.iat to directly access and modify the values
        for cell in path_info:
            i, j = cell['row_idx'], cell['col_idx']
            df.iat[i, j] = f"{df.iat[i, j]}*"  # Append * to the cell value
        return df

    # Apply the modification to the entire DataFrame
    styler = styler.data.copy()  # Work with a copy of the DataFrame to avoid modifying the original
    modified_df = apply_mark(styler)

    # Return the modified Styler object
    return pd.io.formats.style.Styler(modified_df)

# Updated generate_latex_table function to incorporate path_info for marking cells
def generate_latex_table(styler, caption, label, path_info):
    # Apply the style to mark specific cells
    styled = mark_cells_with_asterisk(styler, path_info)
    
    # Generate LaTeX table code from the styled DataFrame
    latex = styled.to_latex()  # escape=False allows special characters like *
    latex = f"\\begin{{table}}[ht]\n\\centering\n{latex}\\caption{{{caption}}}\n\\label{{{label}}}\n\\end{{table}}"
    return latex


# Generate LaTeX codes for multiple tables
def generate_latex_codes_for_tables(tables, path_infos, base_caption, base_label):
    latex_codes = []
    for _, (table, path_info) in enumerate(zip(tables, path_infos)):
        caption = f"{base_caption}"
        label = f"{base_label}"
        latex_code = generate_latex_table(table, caption, label, path_info)
        latex_codes.append(latex_code)
    return latex_codes


def get_output(path_info):
    #common_output = 'We enumerate the relevant row indices, column indices, row names, column names, and their corresponding values.\n\n'
    #common_output += 'Row Index \t Col Index \t Row Name \t Col Name \t Cell Value\n'
    output = []
    digit_to_name = {
        0: '0',
        1: '1',
        2: '2',
        3: '3',
        4: '4',
        5: '5',
        6: '6',
        7: '7',
        8: '8',
        9: '9'
    }


    all_values = []
    for cell in path_info:
        row_idx, col_idx, row_name, col_name, cell_value, path_segment = cell.values()
        output += [{"row index": str(row_idx+1), "col index": str(1+col_idx), "row name": row_name, "col name": col_name, "value": digit_to_name[cell_value]}]
        #common_output += str(row_idx+1) + '\t' + str(col_idx+1) + '\t' + str(row_name) + '\t' + str(col_name) + '\t' + digit_to_name[cell_value] + '\n'
        all_values += [cell_value]
    #common_output += '\n\n'
    total_ = sum([int(v) for v in all_values])
    #common_output += 'Hence, the total value is ' + ' + '.join([str(v) for v in all_values[:-1]]) + ' + ' + str(all_values[-1]) + ' = ' + str(total_) + ".\n\nAnswer: " + str(total_)
    
    return output, str(total_)


def create_and_save_table(df, path, filename):
    df = df.data
    fig, ax = plt.subplots(figsize=(15, 8))  # Adjust the size as needed
    ax.axis('tight')
    ax.axis('off')
    
    def split_column_names(df):
        new_columns = []
        for col in df.columns:
            try:
                if '-' in col:
                    new_columns.append(col.replace('-', '-\n'))
                else:
                    new_columns.append(col)
            except:
                new_columns.append(col)
        df.columns = new_columns
        
        return df

    df = split_column_names(df)
    

    # Dictionary to map digits to their first three letters of their English names
    digit_to_name = {
        0: 'ZERO',
        1: 'ONE',
        2: 'TWO',
        3: 'THREE',
        4: 'FOUR',
        5: 'FIVE',
        6: 'SIX',
        7: 'SEVEN',
        8: 'EIGHT',
        9: 'NINE'
    }

    # Convert the digits in the dataframe
    df_converted = df.applymap(lambda x: digit_to_name[x])
    # Create table
    table = ax.table(cellText=df_converted.values, colLabels=df_converted.columns, rowLabels=df_converted.index, cellLoc='center', loc='center')
    


    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(16)
    
    nrows, ncols = df.shape
    width, height = 1.0 / (ncols + 1), 1.0 / (nrows + 1)

    # Adjust column and row sizes
    path_cells = []
    for entry in path:
        path_cells.append((entry['row_idx'], entry['col_idx']))

    for key, cell in table.get_celld().items():

        cell.set_height(0.1)
        cell.set_width(width)
        
        if key[0] == 0:  # Header cells
            cell.set_facecolor('#40466e')
            cell.set_text_props(weight='bold', color='w')
            
            if '-' not in  cell.get_text().get_text() and len(cell.get_text().get_text()) > 6:
                cell.set_fontsize(14)
        elif key[1] == -1:  # Index cells
            cell.set_facecolor('#40466e')
            cell.set_text_props(weight='bold', color='w')
        elif (key[0]-1, key[1]) in path_cells:  # Path cells   # change: row index starts from 1
            cell.set_facecolor('yellow')
        else:
            cell.set_facecolor('#f5f5f5')
    
    # Ensure table is centered
    #table.scale(1, 15./8.)
    # Adjust layout to remove margins
    # Adjust the layout to avoid clipping
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    plt.tight_layout()
       
    # Convert figure to RGB array
    fig.canvas.draw()
    width, height = fig.canvas.get_width_height()
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    image = image.reshape((height, width, 3))

    pil_image = Image.fromarray(image)
    #pil_image.save('reconstructed_image.png')

    plt.close()
    return image



def convert_to_instruction(all_caption_data):
    all_instructions = []
    for instruction_num, data in enumerate(all_caption_data):
        data["id"] = str(instruction_num) + '_' + str(initial_seed)
        all_instructions += [data]
    return all_instructions


if __name__ == '__main__':
    # Generate multiple tables for each category

    domains = ['business_sales'] 
    domains = {domain: i for i, domain in enumerate(domains)}
    generator_functions = [generate_business_sales_data]
    latex_labels = [
        ("Business Sales Data for products in different months", "tab:business_sales"),
    ]
    all_tables = []
    all_paths = []

    # Generate LaTeX codes for each set of tables
    for domain in domains:
        table, path = generate_tables(generator_functions[domains[domain]], \
                                      args.num_data, \
                                      min_rows=args.min_rows,\
                                      min_cols=args.min_cols, \
                                      max_rows=args.max_rows, \
                                      max_cols=args.max_cols)
        all_tables.append(table)
        all_paths.append(path)


    image_counter = 0
    # OCR Questions
    ocr_ = []
    all_image_RGBs = []
    split_counter = 0
    filename = os.path.abspath(os.path.join(args.output_dir, 'Piecewisepath_TestImage_yellow_{}_split{}_new.npy'.format(initial_seed, split_counter)))


    for domain in domains:
        caption, label = latex_labels[domains[domain]]
        for tab, path_info in tqdm(zip(all_tables[domains[domain]], all_paths[domains[domain]])):
            
            data_ = {}
            
            image_arr = create_and_save_table(tab, path_info, filename)
            all_image_RGBs += [image_arr]
            data_['image_RGB'] = [filename, image_counter]
            image_counter += 1
            if image_counter % 100 == 0:
                image_array = np.array(all_image_RGBs)  # Converts the list to a single 4D numpy array
                np.save(filename, image_array)

                split_counter += 1
                filename = os.path.abspath(os.path.join(args.output_dir, 'Piecewisepath_TestImage_yellow_{}_split{}_new.npy'.format(initial_seed, split_counter)))
                image_counter = 0
                all_image_RGBs = []
            
            latex_table = generate_latex_table(tab, caption, label, path_info)
            latex_table = latex_table.replace("*", " *").replace("\\\\\n", "\\\\\n ")
            data_['text'] = latex_table

            reasoning, answer = get_output(path_info)
            data_["reasoning_steps"] = reasoning
            data_["answer"] = answer

            data_["start_product"] = reasoning[0]["row name"]
            data_["start_month"] = reasoning[0]["col name"]
            data_["end_product"] = reasoning[-1]["row name"]
            data_["end_month"] = reasoning[-1]["col name"]
            
            ocr_ += [data_]

    # Assuming 'images' is a list of (height, width, 3) numpy arrays
    if len(all_image_RGBs) > 0:
        image_array = np.array(all_image_RGBs)  # Converts the list to a single 4D numpy array
        np.save(filename, image_array)


    all_instructions = convert_to_instruction(ocr_)
    with open(os.path.join(args.output_dir, 'raw_{}.json'.format(initial_seed)), 'w') as json_file:
        json.dump(all_instructions, json_file, indent=4)  # indent=4 is used to pretty-# print the JSON

    
    