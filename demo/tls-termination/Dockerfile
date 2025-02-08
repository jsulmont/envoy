FROM nginx:bookworm

ARG TEST_CA_PASSPHRASE
ARG TEST_CLIENT_PASSPHRASE

COPY --chown=www-data:www-data ./nginx.conf /etc/nginx/nginx.conf
COPY --chown=www-data:www-data --chmod=770 ./entrypoint/* /

USER www-data
RUN sh /tls-setup.sh

USER root
CMD ["sh", "/entrypoint.sh"]
