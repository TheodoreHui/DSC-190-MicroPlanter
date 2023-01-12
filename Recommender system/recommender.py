import pandas as pd

weights = {
    "soil_temp": 0.25, 
    "space": 0.1,
    "harvest_days": 0.25,
    "companions": 0.3,
    "STP": 0.1
}

def read_data(file):
    df = pd.read_csv(file)
    df = df.drop(columns = "Unnamed: 0")
    df["S"] = df["S"].map(lambda x: eval(x))
    df["T"] = df["T"].map(lambda x: eval(x))
    df["P"] = df["P"].map(lambda x: eval(x))
    df["avoids"] = df["avoids"].map(lambda x: eval(x))
    df["companions"] = df["companions"].map(lambda x: eval(x))
    return df

def intervalIntersection(A, B):
    # Jaccard Similarity
    a_start, a_end = A[0], A[1]
    b_start, b_end = B[0], B[1]
    if (b_start > a_end) or (a_start > b_end):
        return 0
    o_start = max(a_start, b_start)
    o_end = min(a_end, b_end)
    int_range = max(a_end, b_end) - min(a_start,b_start)
    if int_range == 0:
        return 0
    sim_score = (o_end-o_start)/int_range
    return sim_score

def Jaccard(s1, s2):
    numer = len(s1.intersection(s2))
    denom = len(s1.union(s2))
    if denom == 0:
        return 0
    return numer / denom

def compareSim(plant1, plant2):
    p1_name, p2_name = plant1["plant_name"], plant2["plant_name"]
    if p1_name in plant2["avoids"] or p2_name in plant1["avoids"]:
        return 0
    
    p1_soil_range = (plant1["min_soil_temp"], plant1["max_soil_temp"])
    p2_soil_range = (plant2["min_soil_temp"], plant2["max_soil_temp"])
    soil_sim_score = intervalIntersection(p1_soil_range, p2_soil_range) * weights["soil_temp"]
    
    p1_harvest_range = (plant1["min_harvest_days"], plant1["max_harvest_days"])
    p2_harvest_range = (plant2["min_harvest_days"], plant2["max_harvest_days"])
    harvest_sim_score = intervalIntersection(p1_harvest_range, p2_harvest_range) * weights["harvest_days"]
    
    p1_space_range = (plant1["min_space"], plant1["max_space"])
    p2_space_range = (plant2["min_space"], plant2["max_space"])
    space_sim_score = intervalIntersection(p1_space_range, p2_space_range) * weights["space"]
    
    p1_comp = plant1["companions"]
    p2_comp = plant2["companions"]
    p1_comp_score = 0
    p2_comp_score = 0
    comp_sim_score = 0
    for companion in p2_comp:
        if p1_name in companion or companion in p1_name:
            p1_comp_score = 1
            break
    for companion in p1_comp:
        if p2_name in companion or companion in p2_name:
            p2_comp_score = 1
            break
    comp_sim_score = max(p1_comp_score, p2_comp_score) * weights["companions"]
    
    p1_s = plant1["S"]
    p2_s = plant2["S"]
    p1_t = plant1["T"]
    p2_t = plant2["T"]
    p1_p = plant1["P"]
    p2_p = plant2["P"]
    stp_sim_score = (Jaccard(p1_s, p2_s) + Jaccard(p1_t, p2_t) + Jaccard(p1_p, p2_p)) * weights["STP"]
    
    final_sim_score = soil_sim_score + harvest_sim_score + space_sim_score + comp_sim_score
    return final_sim_score

def mostSimilar(entry, df, N=5):
    similarities = []
    for plant in df.iterrows():
        curr_row = plant[1]
        name = curr_row["plant_name"]
        if name == entry["plant_name"]: 
            continue
        sim = compareSim(entry, curr_row)
        similarities.append((sim,name))
    similarities.sort(reverse=True)
    return similarities[:N]