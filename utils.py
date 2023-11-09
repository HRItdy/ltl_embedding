import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import openai

def find_top_k_similar_error(error_msg, top_k_tasks, retrieve_dict, k):
    error_emb = get_text_embedding(error_msg)
    ori_tasks = []
    errors = []
    revised_tasks = []
    error_embs = []
    for task in top_k_tasks:
        for error in retrieve_dict[task].keys():
            ori_tasks.append(task)
            errors.append(error)
            revised_tasks.append(retrieve_dict[task][error])
            error_embs.append(get_text_embedding(error))

    error_emb = get_text_embedding(error_msg)
    top_k_indices = find_top_k_similar_tasks(error_emb, error_embs, k)
    tasks = [ori_tasks[i] for i in top_k_indices]
    error_msgs = [errors[i] for i in top_k_indices]
    revised_task = [revised_tasks[i] for i in top_k_indices]
    return tasks, error_msgs, revised_task

      
def find_top_k_similar_tasks(emb, emb_list, k):
    # Convert vectors to NumPy arrays
    emb = np.array([emb])
    emb_list = np.array(emb_list)
    # Compute cosine similarity
    similarities = cosine_similarity(emb, emb_list)
    # Get indices of the top k most similar vectors
    top_k_indices = np.argsort(similarities[0])[-k:][::-1]
    return top_k_indices 

def check_violation(task_spec, random_walks, ltl_model):
    satisfy = True
    for walk in random_walks:
        parsed_policy, truth = ltl_model.eval_parse(walk)
        if truth:
            # prompt the LLM to find whether this policy sketch can complete the task, if not, it should generate error message
            ERR_PROMPT = """
                        dsfasdf
                            """
        def get_feedback(task_spec, prompt):
            import re
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt.replace("TASK-TO-BE-PLACED", parsed_policy).replace...task_spec,
                temperature=0.7,
                max_tokens=512,
                top_p=1,
                best_of=1,
                frequency_penalty=0.1,
                presence_penalty=0
                )
            output = response['choices'][0]['text']
            # LTL task should be included in brackets
            satisfy = re.findall(r'\{.*?\}', output)
            message = re.findall(r'\(.*?\)', output)  
            return satisfy, message
        
        satisfy, error_msg = get_feedback(task_spec, ERR_PROMPT)
        if not satisfy:
            # generated task doesn't satisfy task specification, need to be revised, just return
            break
    return satisfy, error_msg

def get_text_embedding(text_to_embed):
	# Embed a line of text
	response = openai.Embedding.create(
    	model= "text-embedding-ada-002",
    	input=[text_to_embed]
	)
	# Extract the AI output embedding as a list of floats
	embedding = response["data"][0]["embedding"]
	return embedding

def get_task_embedding(task_to_embed, env, model):
    env.task = task_to_embed
    activation = {}
    def get_activation(name):
        def hook(model, input, output):
            activation[name] = output.detach()
        return hook
    model.policy.mlp_extractor.ga.register_forward_hook(get_activation('ga'))
    output = model(env.gen_obs())  # is it correct? check the pretrain whats the input of the forward function, and which part is ltl
    embedding = activation['ga']
    return embedding

def rephrase_a_sentence(nl_task, prompt):
    import re
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt.replace("TASK-TO-BE-PLACED", nl_task),
        temperature=0.7,
        max_tokens=512,
        top_p=1,
        best_of=1,
        frequency_penalty=0.1,
        presence_penalty=0
        )
    output = response['choices'][0]['text']
    # LTL task should be included in brackets
    ltl = re.findall(r'\(.*?\)', output)  
    return ltl

def generate_prompt():
    prompt = """"""
    return

def evaluate_prompt():
    pass

def revise_prompt(org, error, k, **kwargs):
    prompt = "The original task is: " + org + "\n" \
             +"Detect error message: " + error + "\n" \
             +"Given the following examples, please give out the revised task without extra explaination: \n" \
             +"".join(["Original task is: "+kwargs['tasks'][i]+ ", error message is: "+kwargs['errors'][i] +", \
                       the revised task is: "+kwargs['revise'][i]+"." for i in k]) + "\n" \
             +"Output:\n"
    return prompt    
    
