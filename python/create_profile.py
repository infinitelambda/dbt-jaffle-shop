
import yaml
import sys
import os

def transform_pk(private_key):
    header, body = private_key.split("----- ")
    header = header + "----- \n"
    body, footer = body.split(" -----")
    footer = "\n-----" + footer
    body = body.replace(" ", "\n")
    private_key = header+ body + footer
    return private_key


def create_profile(env: str):

    with open('profiles/profiles_in.yml') as infile:
        profiles = yaml.full_load(infile)

    with open('profiles/pem.key', 'w') as keyfile:
        private_key = transform_pk(ss.get("private_key"))
        keyfile.write(private_key)


    profiles['default']['target'] = env

    snowflake_settings = profiles['default']['outputs'].pop('env')

    snowflake_settings['account'] = ss.get("account")
    snowflake_settings['user'] = ss.get("username")
    snowflake_settings['password'] = ss.get("password")
    snowflake_settings['private_key_path'] = 'profiles/pem.key'
    snowflake_settings['private_key_passphrase'] = ss.get("private_key_password")
    snowflake_settings['role'] = snowflake_settings['role'][:-3] + env.upper()
    snowflake_settings['database'] = snowflake_settings['database'][:-3] + env.upper()
    snowflake_settings['warehouse'] = snowflake_settings['warehouse'][:-3] + env.upper()

    profiles['default']['outputs'][env] = snowflake_settings

    with open('profiles/profiles.yml', 'w') as outfile:
        yaml.dump(profiles, outfile)


if __name__ == "__main__":
    create_profile(env=sys.argv[1])