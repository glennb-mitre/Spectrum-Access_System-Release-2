#!/usr/bin/env bats

setup() {
    load 'test_helper/bats-support/load'
    load 'test_helper/bats-assert/load'

    DIR="$( cd "$( dirname "$BATS_TEST_FILENAME" )" >/dev/null 2>&1 && pwd )"
    # make executables in src/ visible to PATH
    PATH="$DIR/../src:$PATH"
}


@test "test directory operation pass single character" {
    run ../cert-check.sh -d ../test_files/pass/
    assert_line --index 2 'Certs in the system keychain:'
    assert_line --index 3 'GTS_Root_R1.pem'
    assert_line --index 4 'Certs not in system keychain:'
    assert_line --index 5 'sas.cert'

}

@test "test directory operation pass" {
    run ../cert-check.sh --directory ../test_files/pass/
    assert_line --index 2 'Certs in the system keychain:'
    assert_line --index 3 'GTS_Root_R1.pem'
    assert_line --index 4 'Certs not in system keychain:'
    assert_line --index 5 'sas.cert'

}


@test "test directory operation fail single character" {
    run ../cert-check.sh -d ../test_files/fail/
    assert_line --index 0 'Non certificate items in directory:'
    assert_line --index 1 'non-cert.txt'
    assert_line --index 2 'Expired Certs:'
    assert_line --index 3 'sas_expired.cert'
    assert_line --index 5 'Certs not in system keychain:'
    assert_line --index 6 'cbsd_ca.cert'
    assert_line --index 7 'sas_expired.cert'
}


@test "test directory operation fail" {
    run ../cert-check.sh --directory ../test_files/fail/
    assert_line --index 0 'Non certificate items in directory:'
    assert_line --index 1 'non-cert.txt'
    assert_line --index 2 'Expired Certs:'
    assert_line --index 3 'sas_expired.cert'
    assert_line --index 5 'Certs not in system keychain:'
    assert_line --index 6 'cbsd_ca.cert'
    assert_line --index 7 'sas_expired.cert'
}


@test "interactive operation pass" {
    run ../cert-check.sh <<< '../test_files/pass'
    assert_line --index 3 'Certs in the system keychain:'
    assert_line --index 4 'GTS_Root_R1.pem'
    assert_line --index 5 'Certs not in system keychain:'
    assert_line --index 6 'sas.cert'
}


@test "interactive operation fail" {
    run ../cert-check.sh <<< '../test_files/fail'
    assert_line --index 1 'Non certificate items in directory:'
    assert_line --index 2 'non-cert.txt'
    assert_line --index 3 'Expired Certs:'
    assert_line --index 4 'sas_expired.cert'
    assert_line --index 6 'Certs not in system keychain:'
    assert_line --index 7 'cbsd_ca.cert'
    assert_line --index 8 'sas_expired.cert'
}