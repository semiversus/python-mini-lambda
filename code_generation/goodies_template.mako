# ----
# This file is generated by mini_lambda_methods_generation.py - do not modify it !
# ----
from mini_lambda.main import C, make_lambda_friendly_class, make_lambda_friendly_method
# from warnings import warn

% for o in import_lines:
${o}
% endfor

% for o in to_create:
    % if o.import_line is None or len(o.import_line) == 0:
        % if o.constant_name:
            ## CONSTANT
${o.item_name} = C(${o.constant_name}, '${o.constant_name}')
        % elif o.function_name:
            ## FUNCTION (except Format)
            % if o.function_name != 'Format':
${o.item_name} = make_lambda_friendly_method(${o.function_name}, '${o.function_name}')
            % endif
        % else:
            ## CLASS
${o.item_name} = make_lambda_friendly_class(${o.class_name})
        % endif
    % else:
try:
    ## IMPORT
    ${o.import_line}
        % if o.constant_name:
            ## CONSTANT
    ${o.item_name} = C(${o.constant_name}, '${o.constant_name}')
        % elif o.function_name:
            ## FUNCTION (except Format)
            % if o.function_name != 'Format':
    ${o.item_name} = make_lambda_friendly_method(${o.function_name}, '${o.function_name}')
            % endif
        % else:
            ## CLASS
    ${o.item_name} = make_lambda_friendly_class(${o.class_name})
        % endif
except ImportError as e:
    # new: silently escape, as this is annoying
    # warn("Error performing '${o.import_line}': " + str(e))
    pass
    % endif


% endfor